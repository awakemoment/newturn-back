from django.db import models
from django.utils import timezone
from apps.stocks.models import Stock


class MateAnalysis(models.Model):
    """
    메이트 분석 결과 (캐시)
    """
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='mate_analyses')
    
    # 메이트 정보
    mate_type = models.CharField(
        '메이트 타입',
        max_length=50,
        choices=[
            ('benjamin', '베니 (Benny)'),
            ('fisher', '그로우 (Grow)'),
            ('greenblatt', '매직 (Magic)'),
            ('lynch', '데일리 (Daily)'),
        ]
    )
    
    # 분석 결과
    score = models.IntegerField('점수', help_text='0-100')
    summary = models.CharField('한 줄 요약', max_length=200)
    reason = models.TextField('평가 이유')
    caution = models.TextField('주의사항', blank=True, null=True)
    
    # 세부 점수
    score_detail = models.JSONField('세부 점수', default=dict, blank=True)
    # 예: {"undervalued": 85, "safety": 92, "dividend": 78}
    
    # 메타데이터
    analyzed_at = models.DateTimeField('분석 일시', auto_now=True)
    analysis_version = models.CharField('분석 버전', max_length=20, default='1.0')
    
    class Meta:
        db_table = 'mate_analyses'
        verbose_name = '메이트 분석'
        verbose_name_plural = '메이트 분석'
        unique_together = ['stock', 'mate_type']
        indexes = [
            models.Index(fields=['stock', 'mate_type']),
            models.Index(fields=['score']),
        ]
    
    def __str__(self):
        return f"{self.get_mate_type_display()} - {self.stock.stock_name} ({self.score}점)"


class ProperPrice(models.Model):
    """
    적정가 계산 결과
    """
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='proper_prices')
    mate_type = models.CharField('메이트 타입', max_length=50)
    
    # 적정가
    proper_price = models.DecimalField('적정가', max_digits=15, decimal_places=2)
    current_price = models.DecimalField('현재가', max_digits=15, decimal_places=2)
    gap_ratio = models.DecimalField('괴리율', max_digits=5, decimal_places=2, help_text='%')
    
    # 계산 방법
    calculation_method = models.CharField('계산 방법', max_length=100)
    # 예: "CATEGORY_PER", "DCF", "GRAHAM_FORMULA"
    
    # 백테스팅
    recommended_period_days = models.IntegerField('추천 투자 기간(일)', null=True, blank=True)
    expected_return = models.DecimalField('예상 수익률', max_digits=5, decimal_places=2, null=True, blank=True)
    success_probability = models.DecimalField('수익 확률', max_digits=5, decimal_places=2, null=True, blank=True)
    
    # 메타데이터
    calculated_at = models.DateTimeField('계산 일시', auto_now=True)
    
    class Meta:
        db_table = 'proper_prices'
        verbose_name = '적정가'
        verbose_name_plural = '적정가'
        unique_together = ['stock', 'mate_type']
        indexes = [
            models.Index(fields=['stock', 'gap_ratio']),
        ]
    
    def __str__(self):
        return f"{self.stock.stock_name} - {self.proper_price}원 ({self.gap_ratio}%)"


class QualitativeAnalysis(models.Model):
    """
    정성적 분석 결과 (Claude 직접 분석)
    비즈니스 모델, 경쟁우위, 리스크 등
    """
    stock = models.OneToOneField(Stock, on_delete=models.CASCADE, related_name='qualitative_analysis')
    
    # 비즈니스 모델
    business_model_type = models.CharField('비즈니스 모델 타입', max_length=200)
    business_description = models.TextField('비즈니스 설명')
    understandability_score = models.IntegerField('이해도 점수', help_text='1-10')
    understandability_reason = models.TextField('이해도 이유')
    
    # 경쟁우위 (Moat)
    moat_strength = models.CharField('Moat 강도', max_length=50)
    moat_sustainability = models.IntegerField('Moat 지속성', help_text='1-10')
    moat_factors = models.JSONField('Moat 요소들', default=list)
    # [{"type": "Brand", "strength": 10, "description": "..."}, ...]
    
    # 리스크
    overall_risk_level = models.CharField('종합 리스크 수준', max_length=20)
    risk_score = models.IntegerField('리스크 점수', help_text='0-100, 높을수록 위험')
    top_risks = models.JSONField('주요 리스크', default=list)
    # ["리스크1", "리스크2", "리스크3"]
    
    # 투자 매력도
    investment_score = models.IntegerField('투자 매력도 점수', help_text='0-100')
    investment_grade = models.CharField('투자 등급', max_length=5)
    strengths = models.JSONField('강점', default=list)
    weaknesses = models.JSONField('약점', default=list)
    
    # 지속가능성
    sustainability_score = models.IntegerField('지속가능성 점수', default=0, help_text='1-10')
    
    # 분석 메타데이터
    analyzed_by = models.CharField('분석자', max_length=100, default='Claude AI')
    analyzed_at = models.DateTimeField('분석 일시', auto_now=True)
    analysis_version = models.CharField('분석 버전', max_length=20, default='1.0')
    
    class Meta:
        db_table = 'qualitative_analyses'
        verbose_name = '정성적 분석'
        verbose_name_plural = '정성적 분석'
    
    def __str__(self):
        return f"{self.stock.stock_name} - 정성 분석 ({self.investment_grade})"


class TenKInsight(models.Model):
    """
    10-K에서 추출한 핵심 인사이트
    제품별/지역별 매출, 신규 리스크 등
    """
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='tenk_insights')
    filing_date = models.DateField('Filing 일자')
    fiscal_year = models.IntegerField('회계연도')
    
    # 제품별 매출 (JSON)
    product_revenue = models.JSONField('제품별 매출', default=dict, blank=True)
    # {"iPhone": {"fy2024": 201183, "growth": 6.0}, ...}
    
    # 지역별 매출 (JSON)
    geographic_revenue = models.JSONField('지역별 매출', default=dict, blank=True)
    # {"Americas": {"fy2024": 167000, "growth": 4.0, "share": 45}, ...}
    
    # 주요 비율
    gross_margin = models.DecimalField('매출총이익률', max_digits=5, decimal_places=2, null=True)
    operating_margin = models.DecimalField('영업이익률', max_digits=5, decimal_places=2, null=True)
    net_margin = models.DecimalField('순이익률', max_digits=5, decimal_places=2, null=True)
    
    # R&D 투자
    rd_investment = models.BigIntegerField('R&D 투자', null=True, help_text='Millions')
    rd_as_pct_revenue = models.DecimalField('R&D 비중', max_digits=5, decimal_places=2, null=True)
    
    # 신규 발견 사항
    new_risks = models.JSONField('신규 리스크', default=list, blank=True)
    # ["U.S. Tariffs (2025 Q2)", "China market share decline", ...]
    
    key_changes = models.JSONField('주요 변화', default=list, blank=True)
    # [{"type": "revenue_decline", "region": "China", "impact": -8.0}, ...]
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tenk_insights'
        verbose_name = '10-K 인사이트'
        verbose_name_plural = '10-K 인사이트'
        unique_together = ['stock', 'fiscal_year']
        indexes = [
            models.Index(fields=['stock', '-fiscal_year']),
        ]
    
    def __str__(self):
        return f"{self.stock.stock_name} - FY{self.fiscal_year}"


class ValuationJournalEntry(models.Model):
    """
    투자 결정을 위한 밸류에이션 저널
    """

    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name='valuation_journal_entries'
    )
    entry_date = models.DateField('작성일', default=timezone.now)

    thesis = models.TextField('투자 가설', help_text='이번 투자 판단의 핵심 논리')
    catalysts = models.TextField('주요 촉매', blank=True, null=True)
    risks = models.TextField('주요 리스크', blank=True, null=True)

    current_price = models.DecimalField('현재가', max_digits=15, decimal_places=2)
    my_fair_price = models.DecimalField(
        '내가 생각하는 적정가',
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True
    )
    expected_return = models.DecimalField(
        '기대 수익률',
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='퍼센트(%) 단위'
    )
    conviction_level = models.PositiveSmallIntegerField(
        '확신도',
        default=3,
        help_text='1(낮음) ~ 5(매우 높음)'
    )

    mate_snapshot = models.JSONField(
        '메이트 적정가 스냅샷',
        default=dict,
        blank=True,
        help_text='작성 시점의 네 메이트 적정가 및 괴리율'
    )
    notes = models.TextField('추가 메모', blank=True, null=True)

    review_on = models.DateField('재검토 예정일', blank=True, null=True)
    target_price = models.DecimalField(
        '목표 매도가',
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True
    )

    exit_price = models.DecimalField(
        '실제 청산 가격',
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True
    )
    exit_notes = models.TextField('청산 메모', blank=True, null=True)
    is_closed = models.BooleanField('종료 여부', default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'valuation_journal_entries'
        verbose_name = '밸류에이션 저널'
        verbose_name_plural = '밸류에이션 저널'
        ordering = ['-entry_date', '-created_at']
        indexes = [
            models.Index(fields=['stock', '-entry_date']),
            models.Index(fields=['is_closed']),
        ]

    def __str__(self):
        return f"{self.stock.stock_name} 저널 ({self.entry_date})"

