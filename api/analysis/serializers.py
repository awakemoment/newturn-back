from rest_framework import serializers
from apps.analysis.models import (
    MateAnalysis,
    QualitativeAnalysis,
    TenKInsight,
    ValuationJournalEntry,
)
from apps.stocks.models import Stock


class MateAnalysisSerializer(serializers.ModelSerializer):
    """메이트 분석 Serializer"""
    
    mate_name = serializers.CharField(source='get_mate_type_display', read_only=True)
    
    class Meta:
        model = MateAnalysis
        fields = [
            'id',
            'mate_type',
            'mate_name',
            'score',
            'summary',
            'reason',
            'caution',
            'score_detail',
        ]


class QualitativeAnalysisSerializer(serializers.ModelSerializer):
    """정성적 분석 Serializer"""
    
    class Meta:
        model = QualitativeAnalysis
        fields = [
            'id',
            'business_model_type',
            'business_description',
            'understandability_score',
            'understandability_reason',
            'moat_strength',
            'moat_sustainability',
            'moat_factors',
            'overall_risk_level',
            'risk_score',
            'top_risks',
            'investment_score',
            'investment_grade',
            'strengths',
            'weaknesses',
            'sustainability_score',
            'analyzed_by',
            'analyzed_at',
        ]


class TenKInsightSerializer(serializers.ModelSerializer):
    """10-K 인사이트 Serializer"""
    
    class Meta:
        model = TenKInsight
        fields = [
            'id',
            'filing_date',
            'fiscal_year',
            'product_revenue',
            'geographic_revenue',
            'gross_margin',
            'operating_margin',
            'net_margin',
            'rd_investment',
            'rd_as_pct_revenue',
            'new_risks',
            'key_changes',
            'created_at',
        ]


class StockSummaryField(serializers.PrimaryKeyRelatedField):
    """
    helper field to accept stock_id while exposing summary info
    """

    def to_representation(self, value: Stock):
        return {
            'id': value.id,
            'stock_code': value.stock_code,
            'stock_name': value.stock_name,
            'exchange': value.exchange,
            'sector': value.sector,
        }


class ValuationJournalEntrySerializer(serializers.ModelSerializer):
    stock = StockSummaryField(queryset=Stock.objects.filter(is_active=True))

    class Meta:
        model = ValuationJournalEntry
        fields = [
            'id',
            'stock',
            'entry_date',
            'thesis',
            'catalysts',
            'risks',
            'current_price',
            'my_fair_price',
            'target_price',
            'expected_return',
            'conviction_level',
            'mate_snapshot',
            'notes',
            'review_on',
            'exit_price',
            'exit_notes',
            'is_closed',
            'created_at',
            'updated_at',
        ]
