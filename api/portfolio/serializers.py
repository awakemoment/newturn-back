from rest_framework import serializers
from apps.portfolio.models import Portfolio, PortfolioSnapshot, HoldingSignal
from api.stocks.serializers import StockListSerializer


class PortfolioSnapshotSerializer(serializers.ModelSerializer):
    """
    매수 시점 스냅샷 Serializer
    """
    class Meta:
        model = PortfolioSnapshot
        fields = [
            'id', 'snapshot_date',
            'fcf_margin', 'roe', 'debt_ratio', 'current_ratio',
            'revenue_growth', 'fcf_growth',
            'total_score', 'cashflow_score', 'safety_score', 'growth_score',
            'raw_indicators',
        ]


class HoldingSignalSerializer(serializers.ModelSerializer):
    """
    보유 판단 시그널 Serializer
    """
    signal_display = serializers.CharField(source='get_signal_display', read_only=True)
    
    class Meta:
        model = HoldingSignal
        fields = [
            'id', 'signal', 'signal_display', 'signal_date',
            'current_fcf_margin', 'current_roe', 'current_debt_ratio', 'current_score',
            'score_change', 'fcf_trend', 'warnings', 'recommendation',
        ]


class PortfolioListSerializer(serializers.ModelSerializer):
    """
    포트폴리오 목록용 Serializer
    """
    stock = StockListSerializer(read_only=True)
    stock_code = serializers.CharField(write_only=True, source='stock.stock_code', required=False)
    
    total_investment = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    holding_signals = serializers.SerializerMethodField()
    
    class Meta:
        model = Portfolio
        fields = [
            'id', 'stock', 'stock_code',
            'purchase_date', 'purchase_price', 'shares',
            'total_investment', 'memo',
            'holding_signals',
            'is_sold', 'sold_date', 'sold_price',
            'created_at', 'updated_at',
        ]
    
    def get_holding_signals(self, obj):
        """최신 보유 판단 시그널 목록"""
        signals = obj.signals.all()[:1]  # 최신 1개만
        if signals:
            return [{
                'signal': s.signal,
                'signal_display': s.get_signal_display(),
                'signal_date': s.signal_date,
            } for s in signals]
        return []


class PortfolioDetailSerializer(serializers.ModelSerializer):
    """
    포트폴리오 상세용 Serializer
    """
    stock = StockListSerializer(read_only=True)
    snapshot = PortfolioSnapshotSerializer(read_only=True)
    signals = HoldingSignalSerializer(many=True, read_only=True)
    
    total_investment = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    
    class Meta:
        model = Portfolio
        fields = [
            'id', 'stock', 
            'purchase_date', 'purchase_price', 'shares',
            'total_investment', 'memo', 'sell_criteria',
            'snapshot', 'signals',
            'is_sold', 'sold_date', 'sold_price',
            'created_at', 'updated_at',
        ]


class PortfolioCreateSerializer(serializers.ModelSerializer):
    """
    포트폴리오 생성용 Serializer
    """
    stock_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Portfolio
        fields = [
            'stock_id', 'purchase_date', 'purchase_price', 'shares', 'memo', 'sell_criteria'
        ]
    
    def create(self, validated_data):
        from apps.stocks.models import Stock
        
        stock_id = validated_data.pop('stock_id')
        
        # 종목 조회
        try:
            stock = Stock.objects.get(id=stock_id)
        except Stock.DoesNotExist:
            raise serializers.ValidationError({'stock_id': f'종목 ID {stock_id}를 찾을 수 없습니다.'})
        
        # 포트폴리오 생성 (user는 perform_create에서 save(user=user)로 전달됨)
        validated_data['stock'] = stock
        
        return super().create(validated_data)


# WatchList는 api.watchlist에서 관리

