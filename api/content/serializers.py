from rest_framework import serializers
from apps.content.models import ContentSource, ContentCategory, CuratedContent, WeeklyBrief


class ContentSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentSource
        fields = [
            'id', 'name', 'slug', 'source_type',
            'description', 'website', 'logo_url',
            'is_free', 'price_info',
            'quality_rating', 'reliability',
            'target_audience', 'specialty'
        ]


class ContentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentCategory
        fields = ['id', 'name', 'slug', 'description']


class CuratedContentSerializer(serializers.ModelSerializer):
    source = ContentSourceSerializer(read_only=True)
    category = ContentCategorySerializer(read_only=True)
    
    class Meta:
        model = CuratedContent
        fields = [
            'id', 'title', 'description',
            'source', 'url', 'thumbnail',
            'creator', 'duration',
            'category', 'difficulty', 'tags',
            'curator_note',
            'is_required', 'is_featured',
            'priority', 'views',
        ]


class WeeklyBriefSerializer(serializers.ModelSerializer):
    recommended_contents = CuratedContentSerializer(many=True, read_only=True)
    
    class Meta:
        model = WeeklyBrief
        fields = [
            'id', 'week_number', 'year',
            'start_date', 'end_date',
            'market_summary', 'key_events', 'sector_performance',
            'next_week_watch',
            'recommended_actions', 'risk_alerts',
            'recommended_contents',
            'published_at',
        ]

