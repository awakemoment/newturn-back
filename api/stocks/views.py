"""
주식 데이터 API Views
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
# from core.permissions import require_tier  # 개인 사용: 로그인 불필요
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q, Sum, Avg, Count, F, Case, When, FloatField, IntegerField
from django.db.models.functions import Coalesce

from apps.stocks.models import Stock, StockFinancialRaw, StockPrice
from apps.analysis.models import MateAnalysis
from .serializers import (
    StockListSerializer,
    StockDetailSerializer,
    StockFinancialSerializer,
    StockIndicatorsSerializer,
    StockPriceSerializer,
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class StockViewSet(viewsets.ReadOnlyModelViewSet):
    """
    종목 API
    
    list: 종목 목록 (검색, 필터링)
    retrieve: 종목 상세
    search: 종목 검색
    screen: 스크리닝 (필터링)
    financials: 재무 데이터 (분기별)
    indicators: 핵심 지표 (TTM)
    chart: 차트 데이터
    compare: 종목 비교
    score: 규칙 기반 점수
    """
    queryset = Stock.objects.filter(country='us', is_active=True)
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['stock_code', 'stock_name', 'stock_name_en']
    ordering_fields = ['stock_code', 'stock_name']
    ordering = ['stock_code']
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'search' or self.action == 'screen':
            return StockListSerializer
        elif self.action == 'retrieve':
            return StockDetailSerializer
        return StockListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 거래소 필터
        exchange = self.request.query_params.get('exchange', None)
        if exchange:
            queryset = queryset.filter(exchange=exchange)
        
        # 섹터 필터
        sector = self.request.query_params.get('sector', None)
        if sector:
            queryset = queryset.filter(sector=sector)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        종목 검색
        GET /api/stocks/search/?q=Apple
        """
        query = request.query_params.get('q', '').strip()
        
        if len(query) < 2:
            return Response(
                {'error': '검색어는 2글자 이상이어야 합니다'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 종목명 또는 종목코드로 검색
        stocks = Stock.objects.filter(
            Q(stock_name__icontains=query) |
            Q(stock_code__icontains=query) |
            Q(stock_name_en__icontains=query),
            country='us',
            is_active=True
        ).order_by('stock_name')[:20]
        
        serializer = StockListSerializer(stocks, many=True)
        
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def screen(self, request):
        """
        스크리닝 (필터링)
        
        Query Parameters:
        - min_fcf: 최소 FCF (TTM)
        - min_roe: 최소 ROE (%)
        - max_debt_ratio: 최대 부채비율 (%)
        - min_fcf_margin: 최소 FCF 마진 (%)
        - min_revenue_growth: 최소 매출 성장률 (%)
        - fcf_positive_quarters: FCF 양수 최소 분기 수 (0-20)
        - mate: 메이트 타입 (benjamin, fisher, greenblatt, lynch)
        - min_mate_score: 메이트 최소 점수 (0-100)
        - sort: 정렬 (fcf, roe, fcf_margin, revenue_growth, mate_score)
        """
        # 재무 데이터가 있는 종목만
        stocks_with_data = StockFinancialRaw.objects.filter(
            data_source='EDGAR'
        ).values_list('stock_id', flat=True).distinct()
        
        queryset = Stock.objects.filter(
            id__in=stocks_with_data,
            country='us',
            is_active=True
        )
        
        # 각 종목의 지표 계산 및 필터링
        results = []
        
        # 필터 파라미터
        min_fcf = request.query_params.get('min_fcf')
        min_roe = request.query_params.get('min_roe')
        max_debt_ratio = request.query_params.get('max_debt_ratio')
        min_fcf_margin = request.query_params.get('min_fcf_margin')
        min_revenue_growth = request.query_params.get('min_revenue_growth')
        fcf_positive_quarters = request.query_params.get('fcf_positive_quarters')
        mate_type = request.query_params.get('mate')  # 메이트 필터
        min_mate_score = request.query_params.get('min_mate_score')  # 메이트 최소 점수
        sort_by = request.query_params.get('sort', 'fcf')
        
        for stock in queryset[:500]:  # 성능을 위해 500개로 제한
            try:
                # 최근 4분기
                recent_4q = list(StockFinancialRaw.objects.filter(
                    stock=stock,
                    data_source='EDGAR'
                ).order_by('-disclosure_year', '-disclosure_quarter')[:4])
                
                if len(recent_4q) < 4:
                    continue
                
                # TTM 계산
                ttm_fcf = sum([q.fcf or 0 for q in recent_4q])
                ttm_revenue = sum([q.revenue or 0 for q in recent_4q])
                ttm_net_income = sum([q.net_income or 0 for q in recent_4q])
                
                latest = recent_4q[0]
                
                if not latest.total_equity:
                    continue
                
                # 지표 계산
                fcf_margin = round((ttm_fcf / ttm_revenue) * 100, 2) if ttm_revenue else 0
                roe = round((ttm_net_income / latest.total_equity) * 100, 2)
                debt_ratio = round((latest.total_liabilities / latest.total_equity) * 100, 2) if (latest.total_equity and latest.total_liabilities) else 0
                
                # 성장률
                previous_4q = list(StockFinancialRaw.objects.filter(
                    stock=stock,
                    data_source='EDGAR'
                ).order_by('-disclosure_year', '-disclosure_quarter')[4:8])
                
                revenue_growth = None
                if len(previous_4q) == 4:
                    prev_revenue = sum([q.revenue or 0 for q in previous_4q])
                    if prev_revenue:
                        revenue_growth = round(((ttm_revenue - prev_revenue) / prev_revenue) * 100, 2)
                
                # FCF 양수 분기
                all_financials = list(StockFinancialRaw.objects.filter(
                    stock=stock,
                    data_source='EDGAR'
                ).order_by('-disclosure_year', '-disclosure_quarter')[:20])
                
                fcf_positive_count = len([q for q in all_financials if q.fcf and q.fcf > 0])
                
                # 필터 적용
                if min_fcf and ttm_fcf < float(min_fcf):
                    continue
                if min_roe and roe < float(min_roe):
                    continue
                if max_debt_ratio and debt_ratio > float(max_debt_ratio):
                    continue
                if min_fcf_margin and fcf_margin < float(min_fcf_margin):
                    continue
                if min_revenue_growth and (revenue_growth is None or revenue_growth < float(min_revenue_growth)):
                    continue
                if fcf_positive_quarters and fcf_positive_count < int(fcf_positive_quarters):
                    continue
                
                # 메이트 점수 필터
                mate_score = None
                if mate_type or min_mate_score:
                    from apps.analysis.models import MateAnalysis
                    
                    try:
                        if mate_type:
                            mate_analysis = MateAnalysis.objects.get(
                                stock=stock,
                                mate_type=mate_type
                            )
                            mate_score = mate_analysis.score
                            
                            if min_mate_score and mate_score < int(min_mate_score):
                                continue
                    except MateAnalysis.DoesNotExist:
                        # 메이트 분석이 없으면 건너뛰기
                        continue
                
                result_item = {
                    'stock': StockListSerializer(stock).data,
                    'ttm_fcf': ttm_fcf,
                    'fcf_margin': fcf_margin,
                    'roe': roe,
                    'debt_ratio': debt_ratio,
                    'revenue_growth': revenue_growth,
                    'fcf_positive_quarters': fcf_positive_count,
                }
                
                # 메이트 점수 추가
                if mate_score is not None:
                    result_item['mate_score'] = mate_score
                
                results.append(result_item)
                
            except Exception as e:
                continue
        
        # 정렬
        if sort_by == 'fcf':
            results.sort(key=lambda x: x['ttm_fcf'], reverse=True)
        elif sort_by == 'roe':
            results.sort(key=lambda x: x['roe'], reverse=True)
        elif sort_by == 'fcf_margin':
            results.sort(key=lambda x: x['fcf_margin'], reverse=True)
        elif sort_by == 'revenue_growth':
            results.sort(key=lambda x: x['revenue_growth'] or -999, reverse=True)
        elif sort_by == 'mate_score':
            results.sort(key=lambda x: x.get('mate_score', 0), reverse=True)
        
        # 페이지네이션
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(results, request)
        
        return paginator.get_paginated_response(page)
    
    @action(detail=True, methods=['get'])
    def financials(self, request, pk=None):
        """
        재무 데이터 조회 (분기별)
        
        Query Parameters:
        - limit: 조회할 분기 수 (기본: 20)
        """
        stock = self.get_object()
        limit = int(request.query_params.get('limit', 20))
        
        financials = StockFinancialRaw.objects.filter(
            stock=stock,
            data_source='EDGAR'
        ).order_by('-disclosure_year', '-disclosure_quarter')[:limit]
        
        serializer = StockFinancialSerializer(financials, many=True)
        
        return Response({
            'stock_code': stock.stock_code,
            'stock_name': stock.stock_name,
            'count': len(serializer.data),
            'financials': serializer.data,
        })
    
    @action(detail=True, methods=['get'])
    def indicators(self, request, pk=None):
        """
        핵심 지표 (TTM)
        
        TTM: Trailing Twelve Months (최근 12개월 = 최근 4분기)
        """
        stock = self.get_object()
        
        # 최근 4분기 데이터 (list로 변환)
        recent_4q = list(StockFinancialRaw.objects.filter(
            stock=stock,
            data_source='EDGAR'
        ).order_by('-disclosure_year', '-disclosure_quarter')[:4])
        
        if len(recent_4q) < 4:
            return Response(
                {'error': '재무 데이터가 부족합니다 (최소 4분기 필요)'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # TTM 계산
        ttm_ocf = sum([q.ocf or 0 for q in recent_4q])
        ttm_fcf = sum([q.fcf or 0 for q in recent_4q])
        ttm_capex = sum([abs(q.capex or 0) for q in recent_4q])
        ttm_revenue = sum([q.revenue or 0 for q in recent_4q])
        ttm_net_income = sum([q.net_income or 0 for q in recent_4q])
        
        # 최근 분기 재무상태
        latest = recent_4q[0]
        
        # 지표 계산
        fcf_margin = round((ttm_fcf / ttm_revenue) * 100, 2) if ttm_revenue else 0
        roe = round((ttm_net_income / latest.total_equity) * 100, 2) if latest.total_equity else 0
        debt_ratio = round((latest.total_liabilities / latest.total_equity) * 100, 2) if (latest.total_equity and latest.total_liabilities) else 0
        current_ratio = round((latest.current_assets / latest.current_liabilities) * 100, 2) if latest.current_liabilities else 0
        
        # 성장률 계산 (최근 4분기 vs 전년 동기 4분기)
        previous_4q = list(StockFinancialRaw.objects.filter(
            stock=stock,
            data_source='EDGAR'
        ).order_by('-disclosure_year', '-disclosure_quarter')[4:8])
        
        revenue_growth = None
        fcf_growth = None
        
        if len(previous_4q) == 4:
            prev_revenue = sum([q.revenue or 0 for q in previous_4q])
            prev_fcf = sum([q.fcf or 0 for q in previous_4q])
            
            if prev_revenue:
                revenue_growth = round(((ttm_revenue - prev_revenue) / prev_revenue) * 100, 2)
            if prev_fcf and prev_fcf != 0:
                fcf_growth = round(((ttm_fcf - prev_fcf) / abs(prev_fcf)) * 100, 2)
        
        # 현금흐름 품질
        ocf_to_net_income = round(ttm_ocf / ttm_net_income, 2) if ttm_net_income else None
        
        # FCF 양수 분기 수 (최근 20분기)
        all_financials = list(StockFinancialRaw.objects.filter(
            stock=stock,
            data_source='EDGAR'
        ).order_by('-disclosure_year', '-disclosure_quarter')[:20])
        
        fcf_positive_quarters = len([q for q in all_financials if q.fcf and q.fcf > 0])
        
        # TTM 기간
        ttm_period = f"{recent_4q[-1].disclosure_year}Q{recent_4q[-1].disclosure_quarter}-{recent_4q[0].disclosure_year}Q{recent_4q[0].disclosure_quarter}"
        
        data = {
            'stock_code': stock.stock_code,
            'stock_name': stock.stock_name,
            'ttm_period': ttm_period,
            
            # TTM
            'ttm_ocf': ttm_ocf,
            'ttm_fcf': ttm_fcf,
            'ttm_capex': ttm_capex,
            'ttm_revenue': ttm_revenue,
            'ttm_net_income': ttm_net_income,
            
            # 재무상태
            'total_assets': latest.total_assets,
            'total_liabilities': latest.total_liabilities or 0,
            'total_equity': latest.total_equity,
            
            # 지표
            'fcf_margin': fcf_margin,
            'roe': roe,
            'debt_ratio': debt_ratio,
            'current_ratio': current_ratio,
            
            # 성장률
            'revenue_growth': revenue_growth,
            'fcf_growth': fcf_growth,
            
            # 품질
            'ocf_to_net_income': ocf_to_net_income,
            'fcf_positive_quarters': fcf_positive_quarters,
        }
        
        serializer = StockIndicatorsSerializer(data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def chart(self, request, pk=None):
        """
        차트 데이터 (분기별 트렌드)
        
        Query Parameters:
        - limit: 조회할 분기 수 (기본: 20)
        """
        stock = self.get_object()
        limit = int(request.query_params.get('limit', 20))
        
        financials = StockFinancialRaw.objects.filter(
            stock=stock,
            data_source='EDGAR'
        ).order_by('disclosure_year', 'disclosure_quarter')[:limit]
        
        chart_data = []
        for f in financials:
            chart_data.append({
                'period': f"{f.disclosure_year}Q{f.disclosure_quarter}",
                'date': f.disclosure_date,
                'ocf': f.ocf,
                'fcf': f.fcf,
                'capex': abs(f.capex) if f.capex else None,
                'revenue': f.revenue,
                'net_income': f.net_income,
            })
        
        return Response({
            'stock_code': stock.stock_code,
            'stock_name': stock.stock_name,
            'data': chart_data,
        })
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def compare(self, request):
        """
        종목 비교
        
        POST /api/stocks/compare/
        Body: { "stock_ids": [1, 2, 3] }
        """
        stock_ids = request.data.get('stock_ids', [])
        
        if not stock_ids or len(stock_ids) < 2:
            return Response(
                {'error': '최소 2개 종목을 선택해주세요'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(stock_ids) > 5:
            return Response(
                {'error': '최대 5개 종목까지 비교 가능합니다'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        comparison = []
        
        for stock_id in stock_ids:
            try:
                stock = Stock.objects.get(id=stock_id)
                
                # 지표 계산 (indicators와 동일)
                recent_4q = list(StockFinancialRaw.objects.filter(
                    stock=stock,
                    data_source='EDGAR'
                ).order_by('-disclosure_year', '-disclosure_quarter')[:4])
                
                if len(recent_4q) < 4:
                    comparison.append({
                        'stock': StockListSerializer(stock).data,
                        'error': '재무 데이터 부족'
                    })
                    continue
                
                ttm_fcf = sum([q.fcf or 0 for q in recent_4q])
                ttm_revenue = sum([q.revenue or 0 for q in recent_4q])
                ttm_net_income = sum([q.net_income or 0 for q in recent_4q])
                
                latest = recent_4q[0]
                
                fcf_margin = round((ttm_fcf / ttm_revenue) * 100, 2) if ttm_revenue else 0
                roe = round((ttm_net_income / latest.total_equity) * 100, 2) if latest.total_equity else 0
                debt_ratio = round((latest.total_liabilities / latest.total_equity) * 100, 2) if (latest.total_equity and latest.total_liabilities) else 0
                
                comparison.append({
                    'stock': StockListSerializer(stock).data,
                    'ttm_fcf': ttm_fcf,
                    'ttm_revenue': ttm_revenue,
                    'fcf_margin': fcf_margin,
                    'roe': roe,
                    'debt_ratio': debt_ratio,
                })
                
            except Stock.DoesNotExist:
                continue
        
        return Response({
            'count': len(comparison),
            'comparison': comparison
        })
    
    @action(detail=True, methods=['get'])
    def mates(self, request, pk=None):
        """
        4개 메이트 종합 분석
        
        GET /api/stocks/{id}/mates/
        """
        from core.utils.mate_engines import analyze_with_all_mates
        
        stock = self.get_object()
        
        # 최근 4분기
        recent_4q = list(StockFinancialRaw.objects.filter(
            stock=stock,
            data_source='EDGAR'
        ).order_by('-disclosure_year', '-disclosure_quarter')[:4])
        
        if len(recent_4q) < 4:
            return Response(
                {'error': '재무 데이터가 부족합니다'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 지표 계산
        ttm_ocf = sum([q.ocf or 0 for q in recent_4q])
        ttm_fcf = sum([q.fcf or 0 for q in recent_4q])
        ttm_revenue = sum([q.revenue or 0 for q in recent_4q])
        ttm_net_income = sum([q.net_income or 0 for q in recent_4q])
        
        latest = recent_4q[0]
        
        fcf_margin = round((ttm_fcf / ttm_revenue) * 100, 2) if ttm_revenue else 0
        roe = round((ttm_net_income / latest.total_equity) * 100, 2) if latest.total_equity else 0
        debt_ratio = round((latest.total_liabilities / latest.total_equity) * 100, 2) if (latest.total_equity and latest.total_liabilities) else 0
        current_ratio = round((latest.current_assets / latest.current_liabilities) * 100, 2) if latest.current_liabilities else 0
        
        # 성장률
        previous_4q = list(StockFinancialRaw.objects.filter(
            stock=stock,
            data_source='EDGAR'
        ).order_by('-disclosure_year', '-disclosure_quarter')[4:8])
        
        revenue_growth = None
        fcf_growth = None
        
        if len(previous_4q) == 4:
            prev_revenue = sum([q.revenue or 0 for q in previous_4q])
            prev_fcf = sum([q.fcf or 0 for q in previous_4q])
            
            if prev_revenue:
                revenue_growth = round(((ttm_revenue - prev_revenue) / prev_revenue) * 100, 2)
            if prev_fcf and prev_fcf != 0:
                fcf_growth = round(((ttm_fcf - prev_fcf) / abs(prev_fcf)) * 100, 2)
        
        # FCF 양수 분기
        all_financials = list(StockFinancialRaw.objects.filter(
            stock=stock,
            data_source='EDGAR'
        ).order_by('-disclosure_year', '-disclosure_quarter')[:20])
        
        fcf_positive_quarters = len([q for q in all_financials if q.fcf and q.fcf > 0])
        
        # 지표 딕셔너리
        indicators_dict = {
            'ttm_fcf': ttm_fcf,
            'ttm_revenue': ttm_revenue,
            'ttm_net_income': ttm_net_income,
            'fcf_margin': fcf_margin,
            'roe': roe,
            'debt_ratio': debt_ratio,
            'current_ratio': current_ratio,
            'revenue_growth': revenue_growth,
            'fcf_growth': fcf_growth,
            'fcf_positive_quarters': fcf_positive_quarters,
        }
        
        # 모든 메이트로 분석
        mate_analyses = analyze_with_all_mates(indicators_dict)
        
        return Response({
            'stock_code': stock.stock_code,
            'stock_name': stock.stock_name,
            'mates': mate_analyses,
        })
    
    @action(detail=True, methods=['get'])
    def score(self, request, pk=None):
        """
        규칙 기반 점수 계산
        
        - 현금흐름 점수 (0-100)
        - 안전성 점수 (0-100)
        - 성장성 점수 (0-100)
        - 종합 점수 (0-100)
        """
        stock = self.get_object()
        
        # 최근 4분기
        recent_4q = list(StockFinancialRaw.objects.filter(
            stock=stock,
            data_source='EDGAR'
        ).order_by('-disclosure_year', '-disclosure_quarter')[:4])
        
        if len(recent_4q) < 4:
            return Response(
                {'error': '재무 데이터가 부족합니다'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 지표 계산
        ttm_ocf = sum([q.ocf or 0 for q in recent_4q])
        ttm_fcf = sum([q.fcf or 0 for q in recent_4q])
        ttm_revenue = sum([q.revenue or 0 for q in recent_4q])
        ttm_net_income = sum([q.net_income or 0 for q in recent_4q])
        
        latest = recent_4q[0]
        
        fcf_margin = round((ttm_fcf / ttm_revenue) * 100, 2) if ttm_revenue else 0
        roe = round((ttm_net_income / latest.total_equity) * 100, 2) if latest.total_equity else 0
        debt_ratio = round((latest.total_liabilities / latest.total_equity) * 100, 2) if (latest.total_equity and latest.total_liabilities) else 0
        current_ratio = round((latest.current_assets / latest.current_liabilities) * 100, 2) if latest.current_liabilities else 0
        
        # FCF 양수 분기
        all_financials = list(StockFinancialRaw.objects.filter(
            stock=stock,
            data_source='EDGAR'
        ).order_by('-disclosure_year', '-disclosure_quarter')[:20])
        
        fcf_positive_quarters = len([q for q in all_financials if q.fcf and q.fcf > 0])
        
        # OCF/순이익 비율
        ocf_to_net_income = round(ttm_ocf / ttm_net_income, 2) if ttm_net_income else 0
        
        # 성장률
        previous_4q = list(StockFinancialRaw.objects.filter(
            stock=stock,
            data_source='EDGAR'
        ).order_by('-disclosure_year', '-disclosure_quarter')[4:8])
        
        revenue_growth = 0
        if len(previous_4q) == 4:
            prev_revenue = sum([q.revenue or 0 for q in previous_4q])
            if prev_revenue:
                revenue_growth = round(((ttm_revenue - prev_revenue) / prev_revenue) * 100, 2)
        
        # 점수 계산
        
        # 1. 현금흐름 점수 (0-100)
        cashflow_score = 0
        
        # FCF 양수 분기 (40점)
        if fcf_positive_quarters >= 20:
            cashflow_score += 40
        elif fcf_positive_quarters >= 16:
            cashflow_score += 30
        elif fcf_positive_quarters >= 12:
            cashflow_score += 20
        elif fcf_positive_quarters >= 8:
            cashflow_score += 10
        
        # FCF 마진 (30점)
        if fcf_margin >= 20:
            cashflow_score += 30
        elif fcf_margin >= 15:
            cashflow_score += 25
        elif fcf_margin >= 10:
            cashflow_score += 20
        elif fcf_margin >= 5:
            cashflow_score += 10
        
        # OCF/순이익 비율 (30점)
        if ocf_to_net_income >= 1.5:
            cashflow_score += 30
        elif ocf_to_net_income >= 1.2:
            cashflow_score += 20
        elif ocf_to_net_income >= 1.0:
            cashflow_score += 10
        
        # 2. 안전성 점수 (0-100)
        safety_score = 0
        
        # 부채비율 (50점)
        if debt_ratio <= 30:
            safety_score += 50
        elif debt_ratio <= 50:
            safety_score += 40
        elif debt_ratio <= 100:
            safety_score += 30
        elif debt_ratio <= 150:
            safety_score += 15
        
        # 유동비율 (30점)
        if current_ratio >= 200:
            safety_score += 30
        elif current_ratio >= 150:
            safety_score += 20
        elif current_ratio >= 100:
            safety_score += 10
        
        # FCF > 0 (20점)
        if ttm_fcf > 0:
            safety_score += 20
        
        # 3. 성장성 점수 (0-100)
        growth_score = 0
        
        # ROE (50점)
        if roe >= 25:
            growth_score += 50
        elif roe >= 20:
            growth_score += 40
        elif roe >= 15:
            growth_score += 30
        elif roe >= 10:
            growth_score += 20
        elif roe >= 5:
            growth_score += 10
        
        # 매출 성장률 (50점)
        if revenue_growth >= 20:
            growth_score += 50
        elif revenue_growth >= 15:
            growth_score += 40
        elif revenue_growth >= 10:
            growth_score += 30
        elif revenue_growth >= 5:
            growth_score += 20
        elif revenue_growth >= 0:
            growth_score += 10
        
        # 종합 점수 (평균)
        total_score = round((cashflow_score + safety_score + growth_score) / 3, 1)
        
        # 등급
        if total_score >= 80:
            grade = 'A+'
        elif total_score >= 70:
            grade = 'A'
        elif total_score >= 60:
            grade = 'B+'
        elif total_score >= 50:
            grade = 'B'
        elif total_score >= 40:
            grade = 'C'
        else:
            grade = 'D'
        
        return Response({
            'stock_code': stock.stock_code,
            'stock_name': stock.stock_name,
            'total_score': total_score,
            'grade': grade,
            'scores': {
                'cashflow': cashflow_score,
                'safety': safety_score,
                'growth': growth_score,
            },
            'details': {
                'fcf_positive_quarters': fcf_positive_quarters,
                'fcf_margin': fcf_margin,
                'ocf_to_net_income': ocf_to_net_income,
                'debt_ratio': debt_ratio,
                'current_ratio': current_ratio,
                'ttm_fcf': ttm_fcf,
                'roe': roe,
                'revenue_growth': revenue_growth,
            }
        })
    
    @action(detail=True, methods=['get'])
    # @require_tier('standard')  # 개인 사용: 로그인 불필요
    def tenk_insights(self, request, pk=None):
        """
        10-K 인사이트 (제품별/지역별 매출, 신규 리스크)
        """
        stock = self.get_object()
        
        from apps.analysis.models import TenKInsight
        from api.analysis.serializers import TenKInsightSerializer
        
        insights = TenKInsight.objects.filter(stock=stock).order_by('-fiscal_year')
        
        if not insights.exists():
            return Response(
                {'error': '10-K 인사이트가 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'stock_code': stock.stock_code,
            'stock_name': stock.stock_name,
            'insights': TenKInsightSerializer(insights, many=True).data
        })
    
    @action(detail=False, methods=['get'])
    def screening_table(self, request):
        """
        스크리닝 테이블 뷰 (모든 메이트 점수) - 최적화 버전
        
        Query Parameters:
        - min_avg_score: 평균 점수 최소값 (0-100)
        - min_all_mates: 모든 메이트가 이 점수 이상 (0-100)
        - sort_by: benjamin|fisher|greenblatt|lynch|avg (기본: avg)
        - page: 페이지 번호
        """
        from django.db.models import Avg, Min, Max, Count
        
        # 4개 메이트 분석이 모두 있는 종목만 (집계 쿼리 사용)
        stocks_with_all_mates = MateAnalysis.objects.values('stock_id').annotate(
            mate_count=Count('id')
        ).filter(mate_count=4).values_list('stock_id', flat=True)
        
        # MateAnalysis를 prefetch하여 N+1 문제 해결
        mate_analyses = MateAnalysis.objects.filter(
            stock_id__in=stocks_with_all_mates
        ).select_related('stock').order_by('stock_id', 'mate_type')
        
        # 종목별로 그룹화
        stock_scores = {}
        
        for analysis in mate_analyses:
            stock_id = analysis.stock_id
            
            if stock_id not in stock_scores:
                stock_scores[stock_id] = {
                    'stock': analysis.stock,
                    'benjamin': None,
                    'fisher': None,
                    'greenblatt': None,
                    'lynch': None,
                }
            
            stock_scores[stock_id][analysis.mate_type] = analysis.score
        
        # 평균 계산 및 결과 생성
        results = []
        
        for stock_id, scores in stock_scores.items():
            # 4개가 모두 있는지 확인
            if all(scores[mate] is not None for mate in ['benjamin', 'fisher', 'greenblatt', 'lynch']):
                avg_score = (
                    scores['benjamin'] + 
                    scores['fisher'] + 
                    scores['greenblatt'] + 
                    scores['lynch']
                ) / 4
                
                results.append({
                    'stock': {
                        'id': scores['stock'].id,
                        'stock_code': scores['stock'].stock_code,
                        'stock_name': scores['stock'].stock_name,
                    },
                    'benjamin': scores['benjamin'],
                    'fisher': scores['fisher'],
                    'greenblatt': scores['greenblatt'],
                    'lynch': scores['lynch'],
                    'avg_score': round(avg_score, 1),
                })
        
        # 필터링
        min_avg = request.query_params.get('min_avg_score')
        min_all = request.query_params.get('min_all_mates')
        
        if min_avg:
            results = [r for r in results if r['avg_score'] >= float(min_avg)]
        
        if min_all:
            min_all_val = float(min_all)
            results = [
                r for r in results
                if all(r[mate] >= min_all_val for mate in ['benjamin', 'fisher', 'greenblatt', 'lynch'])
            ]
        
        # 정렬
        sort_by = request.query_params.get('sort_by', 'avg')
        
        if sort_by == 'benjamin':
            results.sort(key=lambda x: x['benjamin'], reverse=True)
        elif sort_by == 'fisher':
            results.sort(key=lambda x: x['fisher'], reverse=True)
        elif sort_by == 'greenblatt':
            results.sort(key=lambda x: x['greenblatt'], reverse=True)
        elif sort_by == 'lynch':
            results.sort(key=lambda x: x['lynch'], reverse=True)
        else:  # avg
            results.sort(key=lambda x: x['avg_score'], reverse=True)
        
        # 페이지네이션
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(results, request)
        
        return paginator.get_paginated_response(page)
