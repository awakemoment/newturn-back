from django.contrib import admin
from .models import Portfolio, PortfolioSnapshot, HoldingSignal


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['user', 'stock', 'purchase_date', 'purchase_price', 'shares', 'is_sold']
    list_filter = ['is_sold', 'purchase_date']
    search_fields = ['user__username', 'stock__stock_name', 'stock__stock_code']
    raw_id_fields = ['user', 'stock']


@admin.register(PortfolioSnapshot)
class PortfolioSnapshotAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'snapshot_date', 'total_score', 'fcf_margin', 'roe']
    raw_id_fields = ['portfolio']


@admin.register(HoldingSignal)
class HoldingSignalAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'signal', 'signal_date', 'current_score', 'score_change']
    list_filter = ['signal', 'signal_date']
    raw_id_fields = ['portfolio']

