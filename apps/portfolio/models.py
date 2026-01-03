from django.db import models
from django.contrib.auth import get_user_model
from apps.stocks.models import Stock

User = get_user_model()


class Portfolio(models.Model):
    """
    포트폴리오 - 보유 종목
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolio')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='portfolio_items')
    
    # 매수 정보
    purchase_date = models.DateField('매수일')
    purchase_price = models.DecimalField('매수가', max_digits=15, decimal_places=2)
    shares = models.DecimalField('보유 수량', max_digits=15, decimal_places=4)
    
    # 메모
    memo = models.TextField('메모', blank=True, null=True, help_text='왜 샀는지, 투자 이유 등')
    
    # 매도 기준 (사용자 설정)
    sell_criteria = models.JSONField('매도 기준', blank=True, null=True, help_text='예: FCF 2분기 연속 10% 감소')
    
    # 메타데이터
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    is_sold = models.BooleanField('매도 완료', default=False)
    sold_date = models.DateField('매도일', null=True, blank=True)
    sold_price = models.DecimalField('매도가', max_digits=15, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'portfolio'
        verbose_name = '포트폴리오'
        verbose_name_plural = '포트폴리오'
        ordering = ['-purchase_date']
        indexes = [
            models.Index(fields=['user', 'is_sold']),
            models.Index(fields=['stock']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.stock.stock_name} ({self.shares}주)"
    
    @property
    def total_investment(self):
        """총 투자금"""
        return float(self.purchase_price) * float(self.shares)


class PortfolioSnapshot(models.Model):
    """
    포트폴리오 스냅샷 - 매수 시점의 재무 지표 저장
    """
    portfolio = models.OneToOneField(Portfolio, on_delete=models.CASCADE, related_name='snapshot')
    
    # 매수 시점 날짜
    snapshot_date = models.DateField('스냅샷 날짜')
    
    # 재무 지표 (매수 시점)
    fcf_margin = models.DecimalField('FCF Margin', max_digits=10, decimal_places=2, null=True, blank=True)
    roe = models.DecimalField('ROE', max_digits=10, decimal_places=2, null=True, blank=True)
    debt_ratio = models.DecimalField('부채비율', max_digits=10, decimal_places=2, null=True, blank=True)
    current_ratio = models.DecimalField('유동비율', max_digits=10, decimal_places=2, null=True, blank=True)
    revenue_growth = models.DecimalField('매출 성장률', max_digits=10, decimal_places=2, null=True, blank=True)
    fcf_growth = models.DecimalField('FCF 성장률', max_digits=10, decimal_places=2, null=True, blank=True)
    
    # 점수 (룰 기반)
    total_score = models.IntegerField('총점', null=True, blank=True)
    cashflow_score = models.IntegerField('현금흐름 점수', null=True, blank=True)
    safety_score = models.IntegerField('안전성 점수', null=True, blank=True)
    growth_score = models.IntegerField('성장성 점수', null=True, blank=True)
    
    # 원본 데이터 (JSON)
    raw_indicators = models.JSONField('원본 지표', blank=True, null=True)
    
    # 메타데이터
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        db_table = 'portfolio_snapshot'
        verbose_name = '포트폴리오 스냅샷'
        verbose_name_plural = '포트폴리오 스냅샷'
    
    def __str__(self):
        return f"{self.portfolio.stock.stock_name} - {self.snapshot_date}"


class HoldingSignal(models.Model):
    """
    보유 판단 시그널 기록
    """
    SIGNAL_CHOICES = [
        ('STRONG_HOLD', '강력 보유'),
        ('HOLD', '보유'),
        ('REVIEW', '재검토'),
        ('CONSIDER_SELL', '매도 고려'),
    ]
    
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='signals')
    
    # 시그널
    signal = models.CharField('시그널', max_length=20, choices=SIGNAL_CHOICES)
    signal_date = models.DateField('시그널 날짜')
    
    # 현재 지표
    current_fcf_margin = models.DecimalField('현재 FCF Margin', max_digits=10, decimal_places=2, null=True)
    current_roe = models.DecimalField('현재 ROE', max_digits=10, decimal_places=2, null=True)
    current_debt_ratio = models.DecimalField('현재 부채비율', max_digits=10, decimal_places=2, null=True)
    current_score = models.IntegerField('현재 점수', null=True)
    
    # 변화
    score_change = models.IntegerField('점수 변화', null=True)
    fcf_trend = models.CharField('FCF 추세', max_length=50, null=True, blank=True)  # 예: "2분기 연속 감소"
    
    # 경고
    warnings = models.JSONField('경고 사항', blank=True, null=True)
    
    # 판단 근거
    recommendation = models.TextField('판단 근거', blank=True, null=True)
    
    # 메타데이터
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        db_table = 'holding_signals'
        verbose_name = '보유 판단 시그널'
        verbose_name_plural = '보유 판단 시그널'
        ordering = ['-signal_date']
        indexes = [
            models.Index(fields=['portfolio', 'signal_date']),
        ]
    
    def __str__(self):
        return f"{self.portfolio.stock.stock_name} - {self.get_signal_display()} ({self.signal_date})"


# WatchList는 apps.watchlist 앱에서 관리

