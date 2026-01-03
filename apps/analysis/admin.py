from django.contrib import admin
from .models import MateAnalysis, ProperPrice, ValuationJournalEntry


@admin.register(MateAnalysis)
class MateAnalysisAdmin(admin.ModelAdmin):
    list_display = ['stock', 'mate_type', 'score', 'summary', 'analyzed_at']
    list_filter = ['mate_type', 'analyzed_at']
    search_fields = ['stock__stock_name', 'stock__stock_code']
    ordering = ['-analyzed_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('stock', 'mate_type', 'analysis_version')
        }),
        ('분석 결과', {
            'fields': ('score', 'summary', 'reason', 'caution')
        }),
        ('세부 점수', {
            'fields': ('score_detail',)
        }),
    )


@admin.register(ProperPrice)
class ProperPriceAdmin(admin.ModelAdmin):
    list_display = ['stock', 'mate_type', 'proper_price', 'current_price', 'gap_ratio', 'calculated_at']
    list_filter = ['mate_type', 'calculated_at']
    search_fields = ['stock__stock_name', 'stock__stock_code']
    ordering = ['-calculated_at']


@admin.register(ValuationJournalEntry)
class ValuationJournalEntryAdmin(admin.ModelAdmin):
    list_display = [
        'stock',
        'entry_date',
        'current_price',
        'my_fair_price',
        'expected_return',
        'conviction_level',
        'review_on',
        'is_closed',
        'updated_at',
    ]
    list_filter = ['is_closed', 'conviction_level', 'entry_date']
    search_fields = ['stock__stock_name', 'stock__stock_code', 'thesis']
    ordering = ['-entry_date', '-created_at']
    readonly_fields = ['created_at', 'updated_at']
