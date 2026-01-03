"""
주식 데이터 Serializers
"""
from rest_framework import serializers
from apps.stocks.models import Stock, StockFinancialRaw, StockPrice


class StockListSerializer(serializers.ModelSerializer):
    """
    종목 리스트용 (간단)
    """
    class Meta:
        model = Stock
        fields = [
            'id',
            'stock_code',
            'stock_name',
            'stock_name_en',
            'exchange',
            'sector',
        ]


class StockDetailSerializer(serializers.ModelSerializer):
    """
    종목 상세 정보
    """
    latest_financials = serializers.SerializerMethodField()
    
    class Meta:
        model = Stock
        fields = [
            'id',
            'stock_code',
            'stock_name',
            'stock_name_en',
            'country',
            'exchange',
            'sector',
            'industry',
            'description',
            'latest_financials',
            'created_at',
            'updated_at',
        ]
    
    def get_latest_financials(self, obj):
        """최근 재무 데이터 요약"""
        latest = obj.financials_raw.filter(
            data_source='EDGAR'
        ).order_by('-disclosure_year', '-disclosure_quarter').first()
        
        if not latest:
            return None
        
        return {
            'year': latest.disclosure_year,
            'quarter': latest.disclosure_quarter,
            'date': latest.disclosure_date,
            'ocf': latest.ocf,
            'fcf': latest.fcf,
            'revenue': latest.revenue,
            'net_income': latest.net_income,
        }


class StockFinancialSerializer(serializers.ModelSerializer):
    """
    재무 데이터 (분기별)
    """
    # 계산 필드
    fcf_margin = serializers.SerializerMethodField()
    roe = serializers.SerializerMethodField()
    debt_ratio = serializers.SerializerMethodField()
    current_ratio = serializers.SerializerMethodField()
    
    class Meta:
        model = StockFinancialRaw
        fields = [
            'id',
            'disclosure_year',
            'disclosure_quarter',
            'disclosure_date',
            
            # 현금흐름
            'ocf',
            'icf',
            'fcf',
            'capex',
            
            # 손익
            'revenue',
            'operating_profit',
            'net_income',
            
            # 재무상태
            'total_assets',
            'current_assets',
            'current_liabilities',
            'total_liabilities',
            'total_equity',
            
            # 배당
            'dividend',
            
            # 계산 필드
            'fcf_margin',
            'roe',
            'debt_ratio',
            'current_ratio',
            
            'data_source',
        ]
    
    def get_fcf_margin(self, obj):
        """FCF 마진 (%)"""
        if obj.revenue and obj.fcf:
            return round((obj.fcf / obj.revenue) * 100, 2)
        return None
    
    def get_roe(self, obj):
        """ROE (%) - 분기 데이터이므로 연간화 필요"""
        if obj.net_income and obj.total_equity:
            # 분기 순이익을 4배해서 연간화
            annual_income = obj.net_income * 4
            return round((annual_income / obj.total_equity) * 100, 2)
        return None
    
    def get_debt_ratio(self, obj):
        """부채비율 (%)"""
        if obj.total_liabilities and obj.total_equity:
            return round((obj.total_liabilities / obj.total_equity) * 100, 2)
        return None
    
    def get_current_ratio(self, obj):
        """유동비율 (%)"""
        if obj.current_assets and obj.current_liabilities:
            return round((obj.current_assets / obj.current_liabilities) * 100, 2)
        return None


class StockIndicatorsSerializer(serializers.Serializer):
    """
    종목 핵심 지표 (TTM)
    """
    stock_code = serializers.CharField()
    stock_name = serializers.CharField()
    
    # TTM (Trailing Twelve Months) 데이터
    ttm_period = serializers.CharField()  # "2024Q1-2024Q4"
    
    # 현금흐름
    ttm_ocf = serializers.IntegerField()
    ttm_fcf = serializers.IntegerField()
    ttm_capex = serializers.IntegerField()
    
    # 손익
    ttm_revenue = serializers.IntegerField()
    ttm_net_income = serializers.IntegerField()
    
    # 최근 분기 재무상태
    total_assets = serializers.IntegerField()
    total_liabilities = serializers.IntegerField()
    total_equity = serializers.IntegerField()
    
    # 지표
    fcf_margin = serializers.FloatField()  # %
    roe = serializers.FloatField()  # %
    debt_ratio = serializers.FloatField()  # %
    current_ratio = serializers.FloatField()  # %
    
    # 성장률 (최근 4분기 vs 전년 동기)
    revenue_growth = serializers.FloatField(allow_null=True)  # %
    fcf_growth = serializers.FloatField(allow_null=True)  # %
    
    # 현금흐름 품질
    ocf_to_net_income = serializers.FloatField(allow_null=True)  # OCF / Net Income
    fcf_positive_quarters = serializers.IntegerField()  # 최근 20분기 중 FCF > 0인 분기 수


class StockPriceSerializer(serializers.ModelSerializer):
    """
    주가 데이터
    """
    class Meta:
        model = StockPrice
        fields = [
            'date',
            'open_price',
            'high_price',
            'low_price',
            'close_price',
            'volume',
            'market_cap',
        ]
