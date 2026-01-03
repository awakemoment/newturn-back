from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from apps.stocks.models import Stock
from apps.analysis.models import MateAnalysis, ProperPrice, ValuationJournalEntry
from .serializers import MateAnalysisSerializer, ValuationJournalEntrySerializer


class AnalysisViewSet(viewsets.ViewSet):
    """
    분석 API
    """
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'], url_path='(?P<stock_code>[^/.]+)')
    def get_analysis(self, request, stock_code=None):
        """
        종목 분석
        GET /api/analysis/{stock_code}/
        
        Response:
        {
            "stock": {...},
            "mate_analyses": [
                {
                    "mate_type": "benjamin",
                    "mate_name": "벤저민 그레이엄",
                    "score": 85,
                    "summary": "저평가된 안전 자산",
                    "reason": "...",
                    "score_detail": {...}
                },
                ...
            ],
            "proper_prices": [...]
        }
        """
        # 종목 조회
        stock = get_object_or_404(Stock, stock_code=stock_code, is_active=True)
        
        # 캐시된 분석 결과 확인
        mate_analyses = MateAnalysis.objects.filter(stock=stock)
        
        if not mate_analyses.exists():
            # 캐시 없으면 새로 분석
            return Response(
                {
                    'message': '분석 중입니다. 잠시 후 다시 시도해주세요.',
                    'status': 'processing'
                },
                status=status.HTTP_202_ACCEPTED
            )
        
        # 적정가 정보
        proper_prices = ProperPrice.objects.filter(stock=stock)
        
        # 응답
        data = {
            'stock': {
                'stock_code': stock.stock_code,
                'stock_name': stock.stock_name,
                'country': stock.country,
                'industry': stock.industry,
            },
            'mate_analyses': MateAnalysisSerializer(mate_analyses, many=True).data,
            'proper_prices': [],  # 추후 구현
        }
        
        return Response(data)
    
    @action(detail=False, methods=['post'])
    def analyze_now(self, request):
        """
        즉시 분석 (캐시 무시)
        POST /api/analysis/analyze_now/
        Body: {"stock_code": "005930"}
        """
        stock_code = request.data.get('stock_code')
        
        if not stock_code:
            return Response(
                {'error': 'stock_code 필수'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stock = get_object_or_404(Stock, stock_code=stock_code, is_active=True)
        
        # TODO: 비동기로 분석 실행 (Celery)
        # 지금은 동기로 (테스트용)
        
        try:
            engine = MateEngine()
            
            # 샘플 데이터 (실제로는 DB에서)
            stock_data = {
                'stock_name': stock.stock_name,
                'pbr': 1.8,
                'debt_ratio': 30.5,
                'dividend_yield': 2.5,
            }
            
            # 벤저민 메이트 분석
            result = engine.analyze(stock_data, mate_type='benjamin')
            
            # DB 저장
            mate_analysis, created = MateAnalysis.objects.update_or_create(
                stock=stock,
                mate_type='benjamin',
                defaults={
                    'score': result['score'],
                    'summary': result['summary'],
                    'reason': result['reason'],
                    'caution': result.get('caution', ''),
                    'score_detail': result.get('score_detail', {}),
                }
            )
            
            return Response({
                'message': '분석 완료',
                'data': MateAnalysisSerializer(mate_analysis).data
            })
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ValuationJournalEntryViewSet(viewsets.ModelViewSet):
    """
    밸류에이션 저널 CRUD
    """

    serializer_class = ValuationJournalEntrySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = ValuationJournalEntry.objects.select_related('stock').order_by('-entry_date', '-created_at')

        stock_code = self.request.query_params.get('stock_code')
        if stock_code:
            queryset = queryset.filter(stock__stock_code__iexact=stock_code)

        is_closed = self.request.query_params.get('is_closed')
        if is_closed is not None:
            if str(is_closed).lower() in ['1', 'true', 'yes']:
                queryset = queryset.filter(is_closed=True)
            else:
                queryset = queryset.filter(is_closed=False)

        return queryset

    def perform_create(self, serializer):
        stock: Stock = serializer.validated_data['stock']
        snapshot = self._build_mate_snapshot(stock)
        serializer.save(mate_snapshot=snapshot)

    def perform_update(self, serializer):
        instance = serializer.instance
        stock = serializer.validated_data.get('stock', instance.stock)
        refresh_snapshot = self._should_refresh_snapshot() or ('stock' in serializer.validated_data)

        if refresh_snapshot:
            snapshot = self._build_mate_snapshot(stock)
            serializer.save(mate_snapshot=snapshot)
        else:
            serializer.save()

    def _build_mate_snapshot(self, stock: Stock):
        snapshot = {}
        proper_prices = ProperPrice.objects.filter(stock=stock)
        for proper in proper_prices:
            snapshot[proper.mate_type] = {
                'proper_price': str(proper.proper_price),
                'current_price': str(proper.current_price),
                'gap_ratio': str(proper.gap_ratio),
                'calculated_at': proper.calculated_at.isoformat() if proper.calculated_at else None,
            }
        return snapshot

    def _should_refresh_snapshot(self):
        value = self.request.data.get('refresh_mate_snapshot')
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        return str(value).lower() in ['1', 'true', 'yes', 'y']
