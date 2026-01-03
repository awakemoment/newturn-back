"""
콘텐츠 큐레이션 API
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from apps.content.models import ContentSource, ContentCategory, CuratedContent, WeeklyBrief
from apps.stocks.models import Stock
from .serializers import ContentSourceSerializer, ContentCategorySerializer, CuratedContentSerializer, WeeklyBriefSerializer


def str_to_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    lowered = value.lower()
    if lowered in {'1', 'true', 'yes', 'y'}:
        return True
    if lowered in {'0', 'false', 'no', 'n'}:
        return False
    return None


class ContentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    콘텐츠 큐레이션 API
    
    - list: 전체 콘텐츠 목록
    - retrieve: 콘텐츠 상세
    - by_stock: 특정 종목의 큐레이션
    - by_category: 카테고리별 콘텐츠
    """
    permission_classes = [AllowAny]
    queryset = CuratedContent.objects.all()
    serializer_class = CuratedContentSerializer
    ordering_fields = ['priority', 'created_at', 'updated_at']
    ordering = ['-priority', '-is_featured', '-created_at']

    def get_queryset(self):
        queryset = (
            CuratedContent.objects.all()
            .select_related('source', 'category')
            .prefetch_related('recommended_for_stocks')
        )

        params = self.request.query_params

        is_featured = str_to_bool(params.get('is_featured'))
        if is_featured is not None:
            queryset = queryset.filter(is_featured=is_featured)

        is_required = str_to_bool(params.get('is_required'))
        if is_required is not None:
            queryset = queryset.filter(is_required=is_required)

        category_slug = params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        source_slug = params.get('source')
        if source_slug:
            queryset = queryset.filter(source__slug=source_slug)

        search = params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)

        ordering_param = params.get('ordering')
        if ordering_param:
            queryset = queryset.order_by(ordering_param)
        else:
            queryset = queryset.order_by('-priority', '-is_featured', '-created_at')

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        total = queryset.count()
        limit = request.query_params.get('limit')
        if limit:
            try:
                limit_value = int(limit)
                if limit_value > 0:
                    queryset = queryset[:limit_value]
            except ValueError:
                pass

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data, 'total': total})
    
    @action(detail=False, methods=['get'], url_path='stocks/(?P<stock_id>[^/.]+)')
    def by_stock(self, request, stock_id=None):
        """
        특정 종목의 큐레이션 콘텐츠
        
        GET /api/content/stocks/{stock_id}/
        """
        stock = get_object_or_404(Stock, id=stock_id)
        
        contents = CuratedContent.objects.filter(
            recommended_for_stocks=stock
        ).select_related('source', 'category').order_by('-priority', '-is_featured', '-is_required')
        
        return Response({
            'stock': {
                'id': stock.id,
                'stock_code': stock.stock_code,
                'stock_name': stock.stock_name,
            },
            'contents': CuratedContentSerializer(contents, many=True).data,
            'total': contents.count(),
        })
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        카테고리별 콘텐츠
        
        GET /api/content/by_category/?category=거시경제
        """
        category_slug = request.query_params.get('category')
        
        if category_slug:
            category = get_object_or_404(ContentCategory, slug=category_slug)
            contents = CuratedContent.objects.filter(
                category=category
            ).select_related('source', 'category').order_by('-priority')
        else:
            contents = CuratedContent.objects.all().select_related('source', 'category').order_by('-priority')
        
        return Response({
            'contents': CuratedContentSerializer(contents, many=True).data,
            'total': contents.count(),
        })


class WeeklyBriefViewSet(viewsets.ReadOnlyModelViewSet):
    """
    주간 브리핑 API
    """
    permission_classes = [AllowAny]
    queryset = WeeklyBrief.objects.filter(is_published=True).order_by('-year', '-week_number')
    serializer_class = WeeklyBriefSerializer
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """최신 브리핑"""
        brief = self.queryset.first()
        
        if not brief:
            return Response(
                {'error': '발행된 브리핑이 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(self.get_serializer(brief).data)

