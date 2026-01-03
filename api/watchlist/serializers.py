from rest_framework import serializers
from apps.watchlist.models import Watchlist
from api.stocks.serializers import StockListSerializer


class WatchlistSerializer(serializers.ModelSerializer):
    """
    관심 종목 Serializer
    """
    stock = StockListSerializer(read_only=True)
    stock_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Watchlist
        fields = [
            'id', 'stock', 'stock_id',
            'memo', 'preferred_mate',
            'is_holding', 'purchase_date', 'purchase_price', 'quantity',
            'alert_enabled', 'alert_gap_ratio',
            'added_at', 'last_checked_at',
        ]
        read_only_fields = ['added_at', 'last_checked_at']
    
    def create(self, validated_data):
        from apps.stocks.models import Stock
        from apps.watchlist.models import Watchlist
        
        stock_id = validated_data.pop('stock_id')
        user = validated_data.get('user')
        
        # 종목 조회
        try:
            stock = Stock.objects.get(id=stock_id)
        except Stock.DoesNotExist:
            raise serializers.ValidationError({'stock_id': f'종목 ID {stock_id}를 찾을 수 없습니다.'})
        
        # 이미 추가되어 있는지 확인 (중복 방지)
        existing = Watchlist.objects.filter(user=user, stock=stock).first()
        if existing:
            # 이미 있으면 기존 것 반환
            return existing
        
        validated_data['stock'] = stock
        return super().create(validated_data)

