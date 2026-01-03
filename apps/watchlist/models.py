from django.db import models
from django.conf import settings
from apps.stocks.models import Stock


class Watchlist(models.Model):
    """
    관심 종목 (나의 투자 클라우드)
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watchlist')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='watchers')
    
    # 메모
    memo = models.TextField('메모', blank=True, null=True)
    
    # 선호 메이트
    preferred_mate = models.CharField('선호 메이트', max_length=50, blank=True, null=True)
    
    # 보유 정보 (선택)
    is_holding = models.BooleanField('보유 여부', default=False)
    purchase_date = models.DateField('매수일', null=True, blank=True)
    purchase_price = models.DecimalField('매수가', max_digits=15, decimal_places=2, null=True, blank=True)
    quantity = models.IntegerField('보유 수량', null=True, blank=True)
    
    # 알림 설정
    alert_enabled = models.BooleanField('알림 활성화', default=True)
    alert_gap_ratio = models.DecimalField(
        '알림 괴리율',
        max_digits=5,
        decimal_places=2,
        default=-10,
        help_text='적정가 대비 괴리율이 이 값 이하일 때 알림 (예: -10%)'
    )
    
    # 메타데이터
    added_at = models.DateTimeField('추가일', auto_now_add=True)
    last_checked_at = models.DateTimeField('마지막 확인', auto_now=True)
    
    class Meta:
        db_table = 'watchlist'
        verbose_name = '관심 종목'
        verbose_name_plural = '관심 종목'
        unique_together = ['user', 'stock']
        indexes = [
            models.Index(fields=['user', 'added_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.stock.stock_name}"

