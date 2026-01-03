"""
계좌 관련 모델

카테고리별 통장, 거래 내역, 절약 리워드, 은행 계좌, 예치금 계좌
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class UserBankAccount(models.Model):
    """사용자 은행 계좌 (Plaid 연동)"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bank_accounts')
    
    # Plaid 정보
    plaid_access_token = models.CharField(max_length=200)  # TODO: 암호화 필요
    plaid_item_id = models.CharField(max_length=100)
    plaid_account_id = models.CharField(max_length=100)
    
    # 계좌 정보
    bank_name = models.CharField(max_length=200)  # "Chase", "Bank of America"
    account_name = models.CharField(max_length=200)  # "Checking Account"
    account_type = models.CharField(max_length=50)  # "checking", "savings"
    account_number_masked = models.CharField(max_length=20)  # "****1234"
    
    # 잔액 정보 (Plaid에서 동기화)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    available_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    
    # 상태
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)  # 주 계좌 여부
    is_simulation = models.BooleanField(default=False)  # 시뮬레이션 계좌 여부
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_bank_accounts'
        unique_together = ['user', 'plaid_account_id']
        verbose_name = '은행 계좌'
        verbose_name_plural = '은행 계좌'
    
    def __str__(self):
        return f"{self.user.username} - {self.bank_name} {self.account_name}"


class CategoryAccount(models.Model):
    """카테고리별 통장 (예: 카페/베이커리 통장)"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='category_accounts')
    name = models.CharField(max_length=100, verbose_name='통장명')  # "카페/베이커리 통장"
    category = models.CharField(max_length=50, verbose_name='카테고리')  # "coffee", "bakery", "snack", "subscription"
    
    # 계좌 잔액
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='현재 잔액')
    total_deposited = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='총 입금액')
    
    # 소비 계획
    monthly_budget = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='월 예산'
    )
    current_month_spent = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name='이번 달 사용액'
    )
    
    # 리워드
    total_savings_reward = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name='총 절약 리워드'
    )
    pending_reward = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name='대기 중인 리워드'
    )
    realized_reward = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name='실현된 리워드'
    )
    
    # 실제 은행 계좌 연동 (Plaid)
    linked_bank_account = models.ForeignKey(
        UserBankAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='category_accounts',
        verbose_name='연동된 은행 계좌'
    )
    auto_sync_enabled = models.BooleanField(default=False, verbose_name='자동 동기화 활성화')
    sync_category_rules = models.JSONField(default=dict, blank=True, verbose_name='카테고리 매핑 규칙')
    
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'category_accounts'
        unique_together = ['user', 'category']
        verbose_name = '카테고리 통장'
        verbose_name_plural = '카테고리 통장'
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    def calculate_monthly_savings(self) -> Decimal:
        """이번 달 절약 금액 계산"""
        if not self.monthly_budget:
            return Decimal('0')
        savings = self.monthly_budget - self.current_month_spent
        return max(savings, Decimal('0'))  # 음수는 0으로


class Transaction(models.Model):
    """거래 내역 (입금/출금)"""
    account = models.ForeignKey(CategoryAccount, on_delete=models.CASCADE, related_name='transactions')
    
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', '입금'),
        ('withdrawal', '출금'),
        ('reward', '리워드'),
        ('investment', '투자'),
        ('sale', '매도'),
        ('bank_sync', '은행 동기화'),
    ]
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, verbose_name='거래 유형')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='금액')
    balance_after = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='거래 후 잔액')
    
    # 출금 시 상세 정보
    merchant_name = models.CharField(max_length=200, blank=True, verbose_name='가맹점명')
    category_detail = models.CharField(max_length=100, blank=True, verbose_name='카테고리 상세')
    
    # 실제 은행 거래 연동
    plaid_transaction_id = models.CharField(max_length=100, blank=True, verbose_name='Plaid 거래 ID')
    bank_transaction_id = models.CharField(max_length=100, blank=True, verbose_name='은행 거래 ID')
    is_synced_from_bank = models.BooleanField(default=False, verbose_name='은행 동기화 여부')
    
    # 메모
    note = models.TextField(blank=True, verbose_name='메모')
    
    transaction_date = models.DateTimeField(auto_now_add=True, verbose_name='거래일시')
    bank_transaction_date = models.DateField(null=True, blank=True, verbose_name='은행 거래일시')
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['plaid_transaction_id']),
            models.Index(fields=['is_synced_from_bank']),
        ]
        verbose_name = '거래 내역'
        verbose_name_plural = '거래 내역'
    
    def __str__(self):
        return f"{self.account.name} - {self.get_transaction_type_display()} ${self.amount}"


class DepositAccount(models.Model):
    """예치금 계좌 (Newturn이 관리하는 중앙 계좌)"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='deposit_accounts')
    
    # 계좌 정보
    account_number = models.CharField(max_length=50, unique=True, verbose_name='계좌번호')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='예치금 잔액')
    total_deposited = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='총 입금액')
    total_withdrawn = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='총 출금액')
    
    # 연동 정보
    alpaca_account_id = models.CharField(max_length=100, blank=True, verbose_name='Alpaca 계좌 ID')
    bank_account_number = models.CharField(max_length=100, blank=True, verbose_name='은행 계좌번호')
    
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'deposit_accounts'
        verbose_name = '예치금 계좌'
        verbose_name_plural = '예치금 계좌'
    
    def __str__(self):
        return f"{self.user.username} - {self.account_number}"


class DepositTransaction(models.Model):
    """예치금 거래 내역"""
    deposit_account = models.ForeignKey(
        DepositAccount, on_delete=models.CASCADE, related_name='transactions', verbose_name='예치금 계좌'
    )
    
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', '입금'),
        ('withdrawal', '출금'),
        ('investment', '투자'),
        ('sale', '매도'),
    ]
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, verbose_name='거래 유형')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='금액')
    balance_after = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='거래 후 잔액')
    
    note = models.TextField(blank=True, verbose_name='메모')
    transaction_date = models.DateTimeField(auto_now_add=True, verbose_name='거래일시')
    
    class Meta:
        db_table = 'deposit_transactions'
        ordering = ['-transaction_date']
        verbose_name = '예치금 거래'
        verbose_name_plural = '예치금 거래'
    
    def __str__(self):
        return f"{self.deposit_account.account_number} - {self.get_transaction_type_display()} ${self.amount}"


class SavingsReward(models.Model):
    """절약 리워드 (주식 투자로 전환)"""
    account = models.ForeignKey(CategoryAccount, on_delete=models.CASCADE, related_name='savings_rewards')
    
    # 절약 정보
    savings_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='절약 금액')
    period_start = models.DateField(verbose_name='기간 시작일')
    period_end = models.DateField(verbose_name='기간 종료일')
    budget = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='예산')
    actual_spent = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='실제 사용액')
    
    # 투자 정보
    stock = models.ForeignKey('stocks.Stock', on_delete=models.PROTECT, related_name='savings_investments')
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='매수 가격')
    purchase_date = models.DateTimeField(verbose_name='매수 일시')
    shares = models.DecimalField(max_digits=15, decimal_places=6, verbose_name='매수 주수')
    
    # 현재 상태
    current_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='현재가')
    current_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='현재 가치')
    return_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='수익률 (%)')
    is_profitable = models.BooleanField(default=False, verbose_name='수익 상태')
    
    # 매도 정보
    can_sell = models.BooleanField(default=False, verbose_name='매도 가능 여부')
    sell_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='매도 가격')
    sell_date = models.DateTimeField(null=True, blank=True, verbose_name='매도일')
    commission = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='수수료')
    net_proceeds = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='순수익')
    
    # 상태
    STATUS_CHOICES = [
        ('pending', '대기 중'),
        ('invested', '투자 중'),
        ('sold', '매도 완료'),
        ('locked', '보유 강제'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='상태')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'savings_rewards'
        ordering = ['-created_at']
        verbose_name = '절약 리워드'
        verbose_name_plural = '절약 리워드'
    
    def __str__(self):
        return f"{self.account.name} - {self.stock.stock_code} ${self.savings_amount}"
    
    def update_current_value(self):
        """현재가 기준으로 가치 업데이트"""
        if not self.current_price or not self.shares:
            return
        
        purchase_cost = self.purchase_price * self.shares
        self.current_value = self.current_price * self.shares
        self.return_rate = ((self.current_value - purchase_cost) / purchase_cost * 100) if purchase_cost > 0 else Decimal('0')
        self.is_profitable = self.current_value > purchase_cost
        self.can_sell = True  # 손실이어도 매도 가능 (경고 메시지는 프론트엔드에서 표시)
        self.save()

