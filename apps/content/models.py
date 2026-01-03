from django.db import models
from apps.stocks.models import Stock


class ContentSource(models.Model):
    """
    콘텐츠 소스 (플랫폼/채널)
    동적으로 추가/수정/삭제 가능
    """
    # 기본 정보
    name = models.CharField('소스명', max_length=100, unique=True)
    slug = models.SlugField('슬러그', max_length=100, unique=True)
    
    # 타입
    SOURCE_TYPE_CHOICES = [
        ('youtube', '유튜브 채널'),
        ('platform', '강의 플랫폼'),
        ('newsletter', '뉴스레터'),
        ('blog', '블로그'),
        ('report', '리포트'),
        ('our_content', '자체 콘텐츠'),
    ]
    source_type = models.CharField('소스 타입', max_length=20, choices=SOURCE_TYPE_CHOICES)
    
    # 상세 정보
    description = models.TextField('설명', blank=True)
    website = models.URLField('웹사이트', blank=True)
    logo_url = models.URLField('로고 URL', blank=True)
    
    # 비용 정보
    is_free = models.BooleanField('무료', default=True)
    price_info = models.CharField('가격 정보', max_length=200, blank=True)
    # 예: "무료", "월 9,900원", "강의당 5-15만원"
    
    # 품질
    quality_rating = models.IntegerField('품질 평가', default=5, help_text='1-5점')
    reliability = models.IntegerField('신뢰도', default=5, help_text='1-5점')
    
    # 특징
    target_audience = models.CharField('대상', max_length=100, blank=True)
    # 예: "초보자", "중급 투자자", "데이터 분석가"
    
    specialty = models.CharField('전문 분야', max_length=100, blank=True)
    # 예: "거시경제", "미국 주식", "차트 분석"
    
    # 메타
    is_active = models.BooleanField('활성화', default=True)
    order = models.IntegerField('순서', default=0)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        db_table = 'content_sources'
        verbose_name = '콘텐츠 소스'
        verbose_name_plural = '콘텐츠 소스'
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


class ContentCategory(models.Model):
    """
    콘텐츠 카테고리
    예: 거시경제, 종목분석, 반도체산업, 재무제표, 포트폴리오 등
    """
    name = models.CharField('카테고리명', max_length=100, unique=True)
    slug = models.SlugField('슬러그', max_length=100, unique=True)
    description = models.TextField('설명', blank=True)
    order = models.IntegerField('순서', default=0)
    is_active = models.BooleanField('활성화', default=True)
    
    class Meta:
        db_table = 'content_categories'
        verbose_name = '콘텐츠 카테고리'
        verbose_name_plural = '콘텐츠 카테고리'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class CuratedContent(models.Model):
    """
    큐레이션된 콘텐츠 (유튜브, 강의, 아티클 등)
    """
    # 기본 정보
    title = models.CharField('제목', max_length=200)
    description = models.TextField('설명')
    
    # 소스 (동적으로 관리)
    source = models.ForeignKey(
        ContentSource,
        on_delete=models.SET_NULL,
        null=True,
        related_name='contents',
        verbose_name='콘텐츠 소스'
    )
    
    # 링크 정보
    url = models.URLField('링크')
    thumbnail = models.URLField('썸네일', blank=True)
    
    # 작성자/채널
    creator = models.CharField('작성자/채널', max_length=100, blank=True)
    duration = models.CharField('길이', max_length=50, blank=True, help_text='예: 45분, 1시간 20분')
    
    # 분류
    category = models.ForeignKey(
        ContentCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='contents',
        verbose_name='카테고리'
    )
    
    # 난이도
    DIFFICULTY_CHOICES = [
        (1, '⭐ 입문'),
        (2, '⭐⭐ 초급'),
        (3, '⭐⭐⭐ 중급'),
        (4, '⭐⭐⭐⭐ 고급'),
        (5, '⭐⭐⭐⭐⭐ 전문가'),
    ]
    difficulty = models.IntegerField('난이도', choices=DIFFICULTY_CHOICES, default=2)
    
    # 태그 (JSON)
    tags = models.JSONField('태그', default=list, blank=True)
    # 예: ["AAPL", "tech", "beginner", "valuation"]
    
    # 추천 대상 종목
    recommended_for_stocks = models.ManyToManyField(
        Stock,
        related_name='recommended_contents',
        blank=True,
        verbose_name='추천 종목'
    )
    
    # 우선순위
    priority = models.IntegerField('우선순위', default=0, help_text='높을수록 먼저 표시')
    is_featured = models.BooleanField('추천', default=False)
    is_required = models.BooleanField('필수', default=False, help_text='종목 이해에 필수')
    
    # 큐레이터 노트
    curator_note = models.TextField(
        '큐레이터 노트',
        blank=True,
        help_text='왜 이 콘텐츠를 추천하는지'
    )
    
    # 통계
    views = models.IntegerField('조회수', default=0)
    
    # 메타데이터
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        db_table = 'curated_contents'
        verbose_name = '큐레이션 콘텐츠'
        verbose_name_plural = '큐레이션 콘텐츠'
        ordering = ['-priority', '-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['source']),
            models.Index(fields=['-priority', '-is_featured']),
        ]
    
    def __str__(self):
        source_name = self.source.name if self.source else '소스 미지정'
        return f"[{source_name}] {self.title}"


class WeeklyBrief(models.Model):
    """
    주간 시장 브리핑 (우리가 직접 작성)
    """
    # 기간
    week_number = models.IntegerField('주차')
    year = models.IntegerField('연도')
    start_date = models.DateField('시작일')
    end_date = models.DateField('종료일')
    
    # 시장 요약
    market_summary = models.TextField('시장 요약')
    # 예: "S&P500 -2.1% (금리 인상 우려 재점화)"
    
    # 주요 이벤트 (JSON)
    key_events = models.JSONField('주요 이벤트', default=list)
    # 예: [
    #   {"title": "NVDA 실적 발표", "description": "매출 +70%, AI 수요 폭발"},
    #   {"title": "유가 급락", "description": "OPEC+ 감산 합의 실패"}
    # ]
    
    # 섹터별 수익률 (JSON)
    sector_performance = models.JSONField('섹터별 수익률', default=dict)
    # 예: {"tech": -3.2, "energy": +2.5, "finance": -1.1}
    
    # 다음 주 관전 포인트
    next_week_watch = models.TextField('다음 주 관전 포인트')
    # 예: "FOMC 회의 (11/12-13), TSLA 실적 발표 (11/14)"
    
    # 우리의 견해
    recommended_actions = models.TextField('추천 액션', blank=True)
    # 예: "단기 조정은 기회. 우량주 중심 분할 매수 전략 권장."
    
    risk_alerts = models.TextField('리스크 알림', blank=True)
    # 예: "금리 변동성 주의. 레버리지 포지션 축소 고려."
    
    # 추천 콘텐츠 (이번 주 필수 시청)
    recommended_contents = models.ManyToManyField(
        CuratedContent,
        related_name='weekly_briefs',
        blank=True,
        verbose_name='추천 콘텐츠'
    )
    
    # 메타데이터
    is_published = models.BooleanField('발행됨', default=False)
    published_at = models.DateTimeField('발행일', null=True, blank=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        db_table = 'weekly_briefs'
        verbose_name = '주간 브리핑'
        verbose_name_plural = '주간 브리핑'
        ordering = ['-year', '-week_number']
        unique_together = ['year', 'week_number']
    
    def __str__(self):
        return f"{self.year}년 {self.week_number}주차 브리핑"

