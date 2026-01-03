from django.contrib import admin
from .models import Stock, StockFinancialRaw, StockPrice


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['stock_code', 'stock_name', 'country', 'exchange', 'industry', 'is_active', 'updated_at']
    list_filter = ['country', 'exchange', 'is_active']
    search_fields = ['stock_code', 'stock_name', 'stock_name_en']
    ordering = ['stock_code']


@admin.register(StockFinancialRaw)
class StockFinancialRawAdmin(admin.ModelAdmin):
    list_display = ['stock', 'disclosure_year', 'disclosure_quarter', 'ocf', 'fcf', 'net_income', 'data_source']
    list_filter = ['disclosure_year', 'data_source', 'stock__country']
    search_fields = ['stock__stock_name', 'stock__stock_code']
    ordering = ['-disclosure_year', '-disclosure_quarter']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('stock', 'disclosure_year', 'disclosure_quarter', 'disclosure_date', 'data_source')
        }),
        ('손익계산서', {
            'fields': ('revenue', 'operating_profit', 'net_income')
        }),
        ('현금흐름표 ⭐', {
            'fields': ('ocf', 'icf', 'fcf', 'capex')
        }),
        ('재무상태표', {
            'fields': ('total_assets', 'current_assets', 'current_liabilities', 'total_liabilities', 'total_equity')
        }),
        ('배당', {
            'fields': ('dividend',)
        }),
    )


@admin.register(StockPrice)
class StockPriceAdmin(admin.ModelAdmin):
    list_display = ['stock', 'date', 'close_price', 'volume', 'market_cap']
    list_filter = ['date', 'stock__country']
    search_fields = ['stock__stock_name', 'stock__stock_code']
    ordering = ['-date']

