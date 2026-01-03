from django.contrib import admin, messages
from django.utils.html import format_html

from .forms import CuratedContentAdminForm
from .models import ContentSource, ContentCategory, CuratedContent, WeeklyBrief


@admin.register(ContentSource)
class ContentSourceAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'source_type',
        'is_free',
        'price_info',
        'quality_rating',
        'reliability',
        'is_active',
        'order'
    ]
    list_filter = ['source_type', 'is_free', 'is_active']
    list_editable = ['is_active', 'order']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'slug', 'source_type', 'description')
        }),
        ('링크', {
            'fields': ('website', 'logo_url')
        }),
        ('비용', {
            'fields': ('is_free', 'price_info')
        }),
        ('품질', {
            'fields': ('quality_rating', 'reliability')
        }),
        ('특성', {
            'fields': ('target_audience', 'specialty')
        }),
        ('설정', {
            'fields': ('is_active', 'order')
        }),
    )
    
    ordering = ['order', 'name']
    list_per_page = 50


@admin.register(ContentCategory)
class ContentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    list_per_page = 50


@admin.register(CuratedContent)
class CuratedContentAdmin(admin.ModelAdmin):
    form = CuratedContentAdminForm
    list_display = [
        'title',
        'source_badge',
        'category_badge',
        'difficulty_display',
        'is_featured',
        'is_required',
        'priority',
        'views',
        'updated_at'
    ]
    list_filter = [
        'source',
        'difficulty', 
        'category', 
        'is_featured', 
        'is_required'
    ]
    list_editable = ['is_featured', 'is_required', 'priority']
    search_fields = ['title', 'description', 'creator', 'tags']
    filter_horizontal = ['recommended_for_stocks']
    autocomplete_fields = ['source', 'category', 'recommended_for_stocks']
    list_display_links = ['title']
    list_per_page = 30
    ordering = ['-priority', '-is_featured', '-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['views', 'created_at', 'updated_at', 'source_preview']
    actions = ['mark_featured', 'mark_required', 'remove_highlights']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'description', 'source', 'source_preview')
        }),
        ('링크', {
            'fields': ('url', 'thumbnail')
        }),
        ('메타데이터', {
            'fields': ('creator', 'duration', 'category', 'difficulty')
        }),
        ('분류 & 추천', {
            'fields': ('tags_text', 'recommended_for_stocks')
        }),
        ('우선순위', {
            'fields': ('priority', 'is_featured', 'is_required')
        }),
        ('큐레이터 노트', {
            'fields': ('curator_note',),
            'classes': ('collapse',)
        }),
        ('기록', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def difficulty_display(self, obj):
        return obj.get_difficulty_display()

    difficulty_display.short_description = '난이도'

    def source_badge(self, obj):
        if not obj.source:
            return format_html('<span style="color:#999">소스 없음</span>')
        return format_html('<strong>{}</strong>', obj.source.name)

    source_badge.short_description = '소스'

    def category_badge(self, obj):
        if not obj.category:
            return format_html('<span style="color:#999">카테고리 없음</span>')
        return obj.category.name

    category_badge.short_description = '카테고리'

    def source_preview(self, obj):
        if obj.pk and obj.url:
            return format_html('<a href="{}" target="_blank">원본 링크 열기</a>', obj.url)
        return '저장 후 링크를 확인할 수 있습니다.'

    source_preview.short_description = '원본 링크 확인'

    @admin.action(description='선택 항목을 추천(Featured)으로 표시')
    def mark_featured(self, request, queryset):
        updated = queryset.update(is_featured=True, priority=10)
        self.message_user(request, f'{updated}개의 콘텐츠가 추천으로 표시되었습니다.', messages.SUCCESS)

    @admin.action(description='선택 항목을 필수 학습으로 표시')
    def mark_required(self, request, queryset):
        updated = queryset.update(is_required=True)
        self.message_user(request, f'{updated}개의 콘텐츠가 필수로 표시되었습니다.', messages.SUCCESS)

    @admin.action(description='선택 항목의 추천/필수 표시 제거')
    def remove_highlights(self, request, queryset):
        updated = queryset.update(is_featured=False, is_required=False)
        self.message_user(request, f'{updated}개의 콘텐츠에서 추천/필수 표시가 제거되었습니다.', messages.INFO)


@admin.register(WeeklyBrief)
class WeeklyBriefAdmin(admin.ModelAdmin):
    list_display = [
        'get_week_display',
        'start_date',
        'end_date',
        'is_published',
        'published_at'
    ]
    list_filter = ['year', 'is_published']
    filter_horizontal = ['recommended_contents']
    
    fieldsets = (
        ('기간', {
            'fields': ('year', 'week_number', 'start_date', 'end_date')
        }),
        ('시장 분석', {
            'fields': ('market_summary', 'key_events', 'sector_performance')
        }),
        ('다음 주', {
            'fields': ('next_week_watch',)
        }),
        ('우리의 견해', {
            'fields': ('recommended_actions', 'risk_alerts')
        }),
        ('추천 콘텐츠', {
            'fields': ('recommended_contents',)
        }),
        ('발행', {
            'fields': ('is_published', 'published_at')
        }),
    )
    
    ordering = ['-year', '-week_number']
    
    def get_week_display(self, obj):
        return f"{obj.year}년 {obj.week_number}주차"
    get_week_display.short_description = '주차'

