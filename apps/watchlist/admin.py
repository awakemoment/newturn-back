from django.contrib import admin
from .models import Watchlist


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'stock', 'is_holding', 'purchase_price', 'alert_enabled', 'added_at']
    list_filter = ['is_holding', 'alert_enabled', 'added_at']
    search_fields = ['user__email', 'stock__stock_name', 'stock__stock_code']
    ordering = ['-added_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'stock', 'memo', 'preferred_mate')
        }),
        ('보유 정보', {
            'fields': ('is_holding', 'purchase_date', 'purchase_price', 'quantity')
        }),
        ('알림 설정', {
            'fields': ('alert_enabled', 'alert_gap_ratio')
        }),
    )

