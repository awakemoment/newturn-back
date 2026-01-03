# 💰 절약 → 주식 투자 시스템 기술 구현 방안

**작성일**: 2024.11.07  
**목적**: 카테고리별 통장 + 절약 리워드 → 주식 투자 시스템 구현

---

## 🎯 **핵심 아이디어**

1. **카테고리별 통장**: 사용자가 돈을 넣고, 카테고리별로 관리 (예: 카페/베이커리 통장)
2. **계획적 소비**: 계획한 금액보다 덜 사용하면 리워드
3. **리워드 = 주식 수익**: 뉴턴 추천 종목이 수익이 나면 매도 → 수수료 제외하고 돌려주기
4. **손실 시 보유 강제**: 수익이 나지 않으면 매도 불가, 보유해야 함
5. **초기 범위**: 본인/지인만 사용 (금융 규제 회피)

---

## 🏗️ **기술 아키텍처**

### **Phase 1: 시뮬레이션 모드 (MVP, 2-3주)**
> 실제 금융 연동 없이 가상 계좌로 시작

### **Phase 2: 증권사 API 연동 (4-6주)**
> 키움/이베스트 등 증권사 API로 실제 매매

### **Phase 3: 전자금융업 신고 (장기)**
> 사용자 확대 시 전자금융업 신고 또는 파트너십

---

## 📊 **Phase 1: 시뮬레이션 모드 (MVP)**

### **1-1. 데이터 모델 설계**

```python
# apps/accounts/models.py

from django.contrib.auth.models import User
from django.db import models
from decimal import Decimal

class CategoryAccount(models.Model):
    """카테고리별 통장 (예: 카페/베이커리 통장)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_accounts')
    name = models.CharField(max_length=100)  # "카페/베이커리 통장"
    category = models.CharField(max_length=50)  # "coffee", "bakery", "snack", "subscription"
    
    # 계좌 잔액
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # 현재 잔액
    total_deposited = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # 총 입금액
    
    # 소비 계획
    monthly_budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  # 월 예산
    current_month_spent = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # 이번 달 사용액
    
    # 리워드
    total_savings_reward = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # 총 절약 리워드
    pending_reward = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # 대기 중인 리워드 (주식 투자 중)
    realized_reward = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # 실현된 리워드 (매도 완료)
    
    # 실제 은행 계좌 연동 (Plaid)
    linked_bank_account = models.ForeignKey(
        'UserBankAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='category_accounts',
        verbose_name='연동된 은행 계좌'
    )
    auto_sync_enabled = models.BooleanField(default=False)  # 자동 동기화 활성화 여부
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'category_accounts'
        unique_together = ['user', 'category']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class Transaction(models.Model):
    """거래 내역 (입금/출금)"""
    account = models.ForeignKey(CategoryAccount, on_delete=models.CASCADE, related_name='transactions')
    
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', '입금'),
        ('withdrawal', '출금'),
        ('reward', '리워드'),
        ('investment', '투자'),
        ('sale', '매도'),
        ('bank_sync', '은행 동기화'),  # Plaid로 자동 동기화된 거래
    ]
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)  # 거래 후 잔액
    
    # 출금 시 상세 정보
    merchant_name = models.CharField(max_length=200, blank=True)  # "스타벅스 강남점"
    category_detail = models.CharField(max_length=100, blank=True)  # "아메리카노"
    
    # 실제 은행 거래 연동
    plaid_transaction_id = models.CharField(max_length=100, blank=True)  # Plaid Transaction ID
    bank_transaction_id = models.CharField(max_length=100, blank=True)  # 은행 거래 ID
    is_synced_from_bank = models.BooleanField(default=False)  # 은행에서 자동 동기화된 거래 여부
    
    # 메모
    note = models.TextField(blank=True)
    
    transaction_date = models.DateTimeField(auto_now_add=True)
    bank_transaction_date = models.DateTimeField(null=True, blank=True)  # 실제 은행 거래 일시
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['plaid_transaction_id']),
            models.Index(fields=['is_synced_from_bank']),
        ]
    
    def __str__(self):
        return f"{self.account.name} - {self.get_transaction_type_display()} {self.amount}원"


class SavingsReward(models.Model):
    """절약 리워드 (주식 투자로 전환)"""
    account = models.ForeignKey(CategoryAccount, on_delete=models.CASCADE, related_name='savings_rewards')
    
    # 절약 정보
    savings_amount = models.DecimalField(max_digits=15, decimal_places=2)  # 절약한 금액
    period_start = models.DateField()  # 기간 시작일
    period_end = models.DateField()  # 기간 종료일
    budget = models.DecimalField(max_digits=15, decimal_places=2)  # 예산
    actual_spent = models.DecimalField(max_digits=15, decimal_places=2)  # 실제 사용액
    
    # 투자 정보
    stock = models.ForeignKey('stocks.Stock', on_delete=models.PROTECT, related_name='savings_investments')
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2)  # 매수 가격
    purchase_date = models.DateTimeField()  # 매수 일시
    shares = models.DecimalField(max_digits=15, decimal_places=6)  # 매수 주수 (소수점 가능)
    
    # 현재 상태
    current_price = models.DecimalField(max_digits=15, decimal_places=2, null=True)  # 현재가
    current_value = models.DecimalField(max_digits=15, decimal_places=2, null=True)  # 현재 가치
    return_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # 수익률 (%)
    is_profitable = models.BooleanField(default=False)  # 수익 상태
    
    # 매도 정보
    can_sell = models.BooleanField(default=False)  # 매도 가능 여부 (수익일 때만 True)
    sell_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    sell_date = models.DateTimeField(null=True, blank=True)
    commission = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # 수수료
    net_proceeds = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  # 순수익 (수수료 제외)
    
    # 상태
    STATUS_CHOICES = [
        ('pending', '대기 중'),  # 절약 완료, 투자 대기
        ('invested', '투자 중'),  # 주식 보유 중
        ('sold', '매도 완료'),  # 수익 실현 완료
        ('locked', '보유 강제'),  # 손실 상태, 매도 불가
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'savings_rewards'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.account.name} - {self.stock.stock_code} {self.savings_amount}원"
    
    def update_current_value(self):
        """현재가 기준으로 가치 업데이트"""
        if not self.current_price or not self.shares:
            return
        
        self.current_value = self.current_price * self.shares
        self.return_rate = ((self.current_value - (self.purchase_price * self.shares)) / (self.purchase_price * self.shares)) * 100
        self.is_profitable = self.current_value > (self.purchase_price * self.shares)
        self.can_sell = self.is_profitable  # 수익일 때만 매도 가능
        self.save()
    
    def sell(self, sell_price: Decimal, commission: Decimal = Decimal('0.0015')):
        """매도 처리 (수익일 때만 가능)"""
        if not self.can_sell:
            raise ValueError("손실 상태에서는 매도할 수 없습니다.")
        
        self.sell_price = sell_price
        self.sell_date = timezone.now()
        self.commission = self.current_value * commission  # 0.15% 수수료
        self.net_proceeds = self.current_value - self.commission
        self.status = 'sold'
        
        # 계좌에 리워드 입금
        self.account.realized_reward += self.net_proceeds
        self.account.pending_reward -= self.savings_amount
        self.account.balance += self.net_proceeds
        self.account.save()
        
        # 거래 내역 기록
        Transaction.objects.create(
            account=self.account,
            transaction_type='sale',
            amount=self.net_proceeds,
            balance_after=self.account.balance,
            note=f"{self.stock.stock_code} 매도 (수익: {self.return_rate:.2f}%)"
        )
        
        self.save()
        return self.net_proceeds
```

---

### **1-2. 비즈니스 로직 (브로커 API 추상화 사용)**

```python
# apps/accounts/services/savings_service.py

from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from apps.stocks.models import Stock, StockPrice
from apps.accounts.models import CategoryAccount, SavingsReward
from apps.accounts.services.trading_service import TradingService

class SavingsInvestmentService:
    """절약 → 투자 서비스"""
    
    @staticmethod
    def calculate_monthly_savings(account: CategoryAccount) -> Decimal:
        """이번 달 절약 금액 계산"""
        if not account.monthly_budget:
            return Decimal('0')
        
        savings = account.monthly_budget - account.current_month_spent
        return max(savings, Decimal('0'))  # 음수는 0으로
    
    @staticmethod
    def create_savings_reward(account: CategoryAccount, stock_id: int, deposit_account=None) -> SavingsReward:
        """
        절약 금액으로 주식 투자 생성
        
        Args:
            account: CategoryAccount
            stock_id: Stock ID
            deposit_account: DepositAccount (None이면 시뮬레이션만)
        """
        savings = SavingsInvestmentService.calculate_monthly_savings(account)
        
        if savings <= 0:
            raise ValueError("절약 금액이 없습니다.")
        
        stock = Stock.objects.get(id=stock_id)
        
        # 브로커 API 사용 (시뮬레이션/실제 자동 선택)
        trading_service = TradingService(deposit_account=deposit_account)
        
        # 현재가 조회
        current_price = trading_service.broker.get_current_price(stock.stock_code)
        
        # 매수 가능 주수 계산 (정수만 가능)
        shares = int(savings / current_price)
        if shares < 1:
            raise ValueError("최소 1주 이상 매수해야 합니다.")
        
        # 리워드 생성
        reward = SavingsReward.objects.create(
            account=account,
            savings_amount=savings,
            period_start=timezone.now().replace(day=1).date(),
            period_end=timezone.now().date(),
            budget=account.monthly_budget,
            actual_spent=account.current_month_spent,
            stock=stock,
            purchase_price=current_price,
            purchase_date=timezone.now(),
            shares=Decimal(str(shares)),
            current_price=current_price,
            status='pending'  # 투자 실행 전
        )
        
        # 실제 투자 실행 (브로커 API)
        reward = trading_service.execute_investment(reward)
        
        # 계좌 업데이트
        account.pending_reward += savings
        account.current_month_spent = Decimal('0')
        account.save()
        
        return reward
    
    @staticmethod
    def update_all_rewards(deposit_account=None):
        """모든 리워드의 현재가 업데이트 (주기적 실행)"""
        # 브로커 API 사용
        trading_service = TradingService(deposit_account=deposit_account)
        trading_service.sync_positions()
    
    @staticmethod
    def sell_reward(reward_id: int, deposit_account=None) -> Decimal:
        """리워드 매도 (수익일 때만)"""
        reward = SavingsReward.objects.get(id=reward_id)
        
        if not reward.can_sell:
            raise ValueError("손실 상태에서는 매도할 수 없습니다. 보유를 유지해야 합니다.")
        
        # 브로커 API 사용
        trading_service = TradingService(deposit_account=deposit_account)
        reward, net_proceeds = trading_service.execute_sale(reward)
        
        return net_proceeds
```

---

### **1-3. API 엔드포인트**

```python
# api/accounts/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from apps.accounts.models import CategoryAccount, Transaction, SavingsReward
from apps.accounts.services import SavingsInvestmentService
from .serializers import CategoryAccountSerializer, TransactionSerializer, SavingsRewardSerializer

class CategoryAccountViewSet(viewsets.ModelViewSet):
    """카테고리별 통장 관리"""
    permission_classes = [IsAuthenticated]
    serializer_class = CategoryAccountSerializer
    
    def get_queryset(self):
        return CategoryAccount.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def deposit(self, request, pk=None):
        """입금"""
        account = self.get_object()
        amount = Decimal(request.data.get('amount', 0))
        
        if amount <= 0:
            return Response({'error': '입금액은 0보다 커야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        account.balance += amount
        account.total_deposited += amount
        account.save()
        
        Transaction.objects.create(
            account=account,
            transaction_type='deposit',
            amount=amount,
            balance_after=account.balance,
            note=request.data.get('note', '')
        )
        
        return Response(CategoryAccountSerializer(account).data)
    
    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        """출금 (소비)"""
        account = self.get_object()
        amount = Decimal(request.data.get('amount', 0))
        merchant_name = request.data.get('merchant_name', '')
        category_detail = request.data.get('category_detail', '')
        
        if amount <= 0:
            return Response({'error': '출금액은 0보다 커야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if account.balance < amount:
            return Response({'error': '잔액이 부족합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        account.balance -= amount
        account.current_month_spent += amount
        account.save()
        
        Transaction.objects.create(
            account=account,
            transaction_type='withdrawal',
            amount=amount,
            balance_after=account.balance,
            merchant_name=merchant_name,
            category_detail=category_detail
        )
        
        return Response(CategoryAccountSerializer(account).data)
    
    @action(detail=True, methods=['get'])
    def monthly_savings(self, request, pk=None):
        """이번 달 절약 금액 조회"""
        account = self.get_object()
        savings = SavingsInvestmentService.calculate_monthly_savings(account)
        
        return Response({
            'savings_amount': float(savings),
            'budget': float(account.monthly_budget) if account.monthly_budget else None,
            'spent': float(account.current_month_spent),
        })
    
    @action(detail=True, methods=['post'])
    def invest_savings(self, request, pk=None):
        """절약 금액으로 주식 투자"""
        account = self.get_object()
        stock_id = request.data.get('stock_id')
        
        try:
            reward = SavingsInvestmentService.create_savings_reward(account, stock_id)
            return Response(SavingsRewardSerializer(reward).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SavingsRewardViewSet(viewsets.ReadOnlyModelViewSet):
    """절약 리워드 (투자) 조회"""
    permission_classes = [IsAuthenticated]
    serializer_class = SavingsRewardSerializer
    
    def get_queryset(self):
        return SavingsReward.objects.filter(account__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def sell(self, request, pk=None):
        """매도 (수익일 때만)"""
        reward = self.get_object()
        
        try:
            net_proceeds = SavingsInvestmentService.sell_reward(reward.id)
            return Response({
                'success': True,
                'net_proceeds': float(net_proceeds),
                'return_rate': float(reward.return_rate),
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def update_prices(self, request):
        """모든 리워드의 현재가 업데이트 (관리자용)"""
        SavingsInvestmentService.update_all_rewards()
        return Response({'success': True})
```

---

### **1-4. 주기적 작업 (Celery)**

```python
# apps/accounts/tasks.py

from celery import shared_task
from apps.accounts.services import SavingsInvestmentService

@shared_task
def update_reward_prices():
    """매일 주가 업데이트 후 리워드 가치 갱신"""
    SavingsInvestmentService.update_all_rewards()
    return "Reward prices updated"
```

---

## 🔌 **Phase 2: 미국 증권사 API 연동**

### **2-1. 증권사 선택 (미국)**

**옵션 1: Alpaca API** ⭐ **추천**
- 장점: 
  - 무료 (Paper Trading + Live Trading)
  - REST API (Python SDK 제공)
  - 커미션 무료 (0% 수수료)
  - 미국 주식 전용 (우리 서비스에 적합)
  - Paper Trading으로 테스트 가능
- 단점: 미국 주식만 지원
- API 문서: https://alpaca.markets/docs/
- 가입: https://alpaca.markets/

**옵션 2: Interactive Brokers (IBKR) API**
- 장점: 글로벌 주식 지원, 낮은 수수료
- 단점: API 복잡, 수수료 있음
- API 문서: https://www.interactivebrokers.com/en/index.php?f=5041

**옵션 3: TD Ameritrade API (Schwab 통합)**
- 장점: 대형 증권사, 안정적
- 단점: API 복잡, 수수료 있음
- API 문서: https://developer.tdameritrade.com/

**추천: Alpaca API**
- REST API로 구현 간단
- Paper Trading으로 안전하게 테스트
- 커미션 무료로 사용자에게 유리
- Python SDK 제공으로 개발 편의성 높음

---

### **2-2. Alpaca API 래퍼**

```python
# apps/broker/alpaca_api.py

import os
from decimal import Decimal
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

class AlpacaAPI:
    """Alpaca API 래퍼"""
    
    def __init__(self, api_key: str = None, secret_key: str = None, paper: bool = True):
        """
        Alpaca API 초기화
        
        Args:
            api_key: Alpaca API Key (환경변수에서 가져옴)
            secret_key: Alpaca Secret Key (환경변수에서 가져옴)
            paper: Paper Trading 모드 (True) 또는 Live Trading (False)
        """
        self.api_key = api_key or os.getenv('ALPACA_API_KEY')
        self.secret_key = secret_key or os.getenv('ALPACA_SECRET_KEY')
        self.paper = paper
        
        # Trading Client (매수/매도)
        self.trading_client = TradingClient(
            api_key=self.api_key,
            secret_key=self.secret_key,
            paper=paper  # Paper Trading 모드
        )
        
        # Data Client (주가 조회)
        self.data_client = StockHistoricalDataClient(
            api_key=self.api_key,
            secret_key=self.secret_key
        )
    
    def get_current_price(self, symbol: str) -> Decimal:
        """현재가 조회"""
        try:
            request = StockLatestQuoteRequest(symbol_or_symbols=[symbol])
            latest_quote = self.data_client.get_stock_latest_quote(request)
            
            if symbol in latest_quote:
                # Bid와 Ask의 중간가 사용
                bid = Decimal(str(latest_quote[symbol].bid_price))
                ask = Decimal(str(latest_quote[symbol].ask_price))
                return (bid + ask) / 2
            else:
                raise ValueError(f"주가 데이터를 찾을 수 없습니다: {symbol}")
        except Exception as e:
            raise ValueError(f"주가 조회 실패: {str(e)}")
    
    def buy_stock(self, symbol: str, quantity: Decimal, order_type: str = 'market') -> dict:
        """
        주식 매수
        
        Args:
            symbol: 종목 코드 (예: 'AAPL', 'NVDA')
            quantity: 매수 주수
            order_type: 'market' (시장가) 또는 'limit' (지정가)
        
        Returns:
            {
                'order_id': str,
                'status': str,
                'filled_qty': Decimal,
                'filled_avg_price': Decimal,
                'commission': Decimal
            }
        """
        try:
            # Alpaca는 주수를 정수로 요구 (소수점 불가)
            qty = int(quantity)
            if qty <= 0:
                raise ValueError("매수 주수는 1주 이상이어야 합니다.")
            
            if order_type == 'market':
                order_request = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                )
            else:
                # Limit order는 가격 필요
                current_price = self.get_current_price(symbol)
                order_request = LimitOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY,
                    limit_price=float(current_price)
                )
            
            order = self.trading_client.submit_order(order_request)
            
            return {
                'order_id': order.id,
                'status': order.status.value,
                'filled_qty': Decimal(str(order.filled_qty or 0)),
                'filled_avg_price': Decimal(str(order.filled_avg_price or 0)),
                'commission': Decimal('0')  # Alpaca는 커미션 무료
            }
        except Exception as e:
            raise ValueError(f"매수 주문 실패: {str(e)}")
    
    def sell_stock(self, symbol: str, quantity: Decimal, order_type: str = 'market') -> dict:
        """
        주식 매도
        
        Args:
            symbol: 종목 코드
            quantity: 매도 주수
            order_type: 'market' (시장가) 또는 'limit' (지정가)
        
        Returns:
            {
                'order_id': str,
                'status': str,
                'filled_qty': Decimal,
                'filled_avg_price': Decimal,
                'commission': Decimal
            }
        """
        try:
            qty = int(quantity)
            if qty <= 0:
                raise ValueError("매도 주수는 1주 이상이어야 합니다.")
            
            if order_type == 'market':
                order_request = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                )
            else:
                current_price = self.get_current_price(symbol)
                order_request = LimitOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY,
                    limit_price=float(current_price)
                )
            
            order = self.trading_client.submit_order(order_request)
            
            return {
                'order_id': order.id,
                'status': order.status.value,
                'filled_qty': Decimal(str(order.filled_qty or 0)),
                'filled_avg_price': Decimal(str(order.filled_avg_price or 0)),
                'commission': Decimal('0')  # Alpaca는 커미션 무료
            }
        except Exception as e:
            raise ValueError(f"매도 주문 실패: {str(e)}")
    
    def get_commission(self, amount: Decimal) -> Decimal:
        """
        수수료 계산 (Alpaca는 커미션 무료)
        
        참고: 실제로는 SEC Fee (매도 시 $0.0000229 per share)가 있지만
        소액 투자에서는 무시 가능
        """
        return Decimal('0')
    
    def get_account_balance(self) -> Decimal:
        """계좌 잔액 조회"""
        account = self.trading_client.get_account()
        return Decimal(str(account.cash))
    
    def get_positions(self) -> list:
        """보유 포지션 조회"""
        positions = self.trading_client.get_all_positions()
        return [
            {
                'symbol': pos.symbol,
                'qty': Decimal(str(pos.qty)),
                'avg_entry_price': Decimal(str(pos.avg_entry_price)),
                'current_price': Decimal(str(pos.current_price)),
                'market_value': Decimal(str(pos.market_value)),
            }
            for pos in positions
        ]
```

---

### **2-3. 예치금 관리 시스템**

```python
# apps/accounts/models.py (추가)

class DepositAccount(models.Model):
    """예치금 계좌 (Newturn이 관리하는 중앙 계좌)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deposit_accounts')
    
    # 계좌 정보
    account_number = models.CharField(max_length=50, unique=True)  # 가상 계좌번호
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # 예치금 잔액
    total_deposited = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # 총 입금액
    total_withdrawn = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # 총 출금액
    
    # 연동 정보
    alpaca_account_id = models.CharField(max_length=100, blank=True)  # Alpaca 계좌 ID
    bank_account_number = models.CharField(max_length=100, blank=True)  # 미국 은행 계좌번호 (선택)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'deposit_accounts'
    
    def __str__(self):
        return f"{self.user.username} - {self.account_number}"


class DepositTransaction(models.Model):
    """예치금 거래 내역"""
    account = models.ForeignKey(DepositAccount, on_delete=models.CASCADE, related_name='deposit_transactions')
    
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', '입금'),
        ('withdrawal', '출금'),
        ('investment', '투자'),
        ('sale', '매도'),
        ('dividend', '배당'),
    ]
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    
    # 외부 거래 ID
    external_transaction_id = models.CharField(max_length=100, blank=True)  # Alpaca Order ID 등
    bank_transaction_id = models.CharField(max_length=100, blank=True)  # 은행 거래 ID
    
    note = models.TextField(blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'deposit_transactions'
        ordering = ['-transaction_date']
```

### **2-4. 실제 매매 로직 (Alpaca 연동)**

```python
# apps/accounts/services.py (확장)

from apps.broker.alpaca_api import AlpacaAPI

class RealTradingService:
    """Alpaca API를 통한 실제 매매"""
    
    def __init__(self, user=None):
        """
        Args:
            user: 사용자 객체 (각 사용자별 Alpaca 계좌 사용 시)
        """
        # 환경변수에서 Alpaca API 키 가져오기
        # 또는 사용자별로 다른 API 키 사용 가능
        self.broker = AlpacaAPI(paper=False)  # Live Trading 모드
        self.user = user
    
    def execute_investment(self, reward: SavingsReward, deposit_account: DepositAccount):
        """
        실제 주식 매수 실행 (예치금에서 차감)
        
        Args:
            reward: SavingsReward 객체
            deposit_account: 예치금 계좌
        """
        # 1. 예치금 잔액 확인
        if deposit_account.balance < reward.savings_amount:
            raise ValueError("예치금 잔액이 부족합니다.")
        
        # 2. 현재가 조회
        symbol = reward.stock.stock_code  # 'AAPL', 'NVDA' 등
        current_price = self.broker.get_current_price(symbol)
        
        # 3. 매수 가능 주수 계산 (Alpaca는 정수 주수만 가능)
        shares = int(reward.savings_amount / current_price)
        if shares < 1:
            raise ValueError("최소 1주 이상 매수해야 합니다.")
        
        # 4. 실제 매수 주문 (Alpaca)
        result = self.broker.buy_stock(
            symbol=symbol,
            quantity=Decimal(str(shares)),
            order_type='market'
        )
        
        # 5. 실제 매수 가격으로 재계산
        actual_cost = result['filled_avg_price'] * result['filled_qty']
        commission = result['commission']
        
        # 6. 예치금 차감
        deposit_account.balance -= actual_cost + commission
        deposit_account.save()
        
        # 7. 거래 내역 기록
        DepositTransaction.objects.create(
            account=deposit_account,
            transaction_type='investment',
            amount=-(actual_cost + commission),
            balance_after=deposit_account.balance,
            external_transaction_id=result['order_id'],
            note=f"{symbol} {shares}주 매수"
        )
        
        # 8. 리워드 업데이트
        reward.purchase_price = result['filled_avg_price']
        reward.shares = result['filled_qty']
        reward.status = 'invested'
        reward.save()
        
        return reward
    
    def execute_sale(self, reward: SavingsReward, deposit_account: DepositAccount):
        """
        실제 주식 매도 실행 (수익일 때만, 예치금에 입금)
        
        Args:
            reward: SavingsReward 객체
            deposit_account: 예치금 계좌
        """
        if not reward.can_sell:
            raise ValueError("손실 상태에서는 매도할 수 없습니다. 보유를 유지해야 합니다.")
        
        # 1. 현재가 조회
        symbol = reward.stock.stock_code
        current_price = self.broker.get_current_price(symbol)
        
        # 2. 실제 매도 주문 (Alpaca)
        result = self.broker.sell_stock(
            symbol=symbol,
            quantity=reward.shares,
            order_type='market'
        )
        
        # 3. 매도 금액 계산
        sale_proceeds = result['filled_avg_price'] * result['filled_qty']
        commission = result['commission']
        net_proceeds = sale_proceeds - commission
        
        # 4. 예치금 입금
        deposit_account.balance += net_proceeds
        deposit_account.total_withdrawn += net_proceeds  # 출금 가능 금액 증가
        deposit_account.save()
        
        # 5. 거래 내역 기록
        DepositTransaction.objects.create(
            account=deposit_account,
            transaction_type='sale',
            amount=net_proceeds,
            balance_after=deposit_account.balance,
            external_transaction_id=result['order_id'],
            note=f"{symbol} {reward.shares}주 매도 (수익: {reward.return_rate:.2f}%)"
        )
        
        # 6. 리워드 업데이트
        reward.sell_price = result['filled_avg_price']
        reward.sell_date = timezone.now()
        reward.commission = commission
        reward.net_proceeds = net_proceeds
        reward.status = 'sold'
        reward.save()
        
        # 7. 카테고리 계좌에 리워드 반영
        reward.account.realized_reward += net_proceeds
        reward.account.pending_reward -= reward.savings_amount
        reward.account.save()
        
        return reward, net_proceeds
    
    def sync_positions(self, deposit_account: DepositAccount):
        """Alpaca 계좌의 실제 포지션과 DB 동기화"""
        positions = self.broker.get_positions()
        
        # DB의 모든 투자 중인 리워드 업데이트
        rewards = SavingsReward.objects.filter(
            account__user=deposit_account.user,
            status='invested'
        )
        
        for reward in rewards:
            symbol = reward.stock.stock_code
            position = next((p for p in positions if p['symbol'] == symbol), None)
            
            if position:
                reward.current_price = position['current_price']
                reward.update_current_value()
```

---

## 🚨 **법적 고려사항 (미국 기준)**

### **현재 단계 (본인/지인만 사용)**
- ✅ **SEC 규제 회피**: 불특정 다수에게 투자 자문 서비스 제공하지 않음
- ✅ **예치금 관리**: 개인/지인 범위 내에서는 규제 회피 가능
- ⚠️ **주의**: 사용자 확대 시 SEC 등록 필요

### **SEC 등록 조건 (Investment Adviser)**
- **등록 필요 조건**:
  - 불특정 다수에게 투자 자문 제공
  - 고객 자금 관리 (예치금, 투자 실행)
  - 연간 관리 자산(AUM) $100M 이상 또는 특정 주에서 운영
- **등록 기관**: SEC 또는 주 금융당국
- **비용**: 약 $10,000 ~ $50,000 (변호사 비용 포함)
- **기간**: 3-6개월

### **예치금 관리 시 주의사항**
1. **자금 분리**: 고객 자금과 운영 자금 분리 (Segregated Account)
2. **투명성**: 모든 거래 내역 기록 및 고객에게 공개
3. **보험**: SIPC 보험 가입 고려 (Alpaca는 자동 보험)
4. **세금**: 고객별 세금 신고 지원 (1099 발급)

### **Alpaca 사용 시 장점**
- ✅ **SIPC 보험**: 최대 $500,000 보호
- ✅ **자금 분리**: Alpaca가 자동으로 고객 자금 분리 관리
- ✅ **투명성**: 모든 거래 내역 API로 조회 가능

### **대안: 파트너십**
- Alpaca와 제휴하여 White-label 솔루션 사용
- 또는 다른 RIA (Registered Investment Adviser)와 파트너십

---

## 📋 **구현 로드맵**

### **Phase 1: 시뮬레이션 MVP (2-3주)**
- [ ] 데이터 모델 생성 (`CategoryAccount`, `SavingsReward`, `Transaction`)
- [ ] API 엔드포인트 구현
- [ ] 프론트엔드 UI (통장 관리, 절약 추적, 투자 현황)
- [ ] 주가 업데이트 스케줄러 (Celery)

### **Phase 2: Alpaca API 연동 & 예치금 시스템 (4-6주)**
- [ ] Alpaca API 계정 생성 및 설정
- [ ] Alpaca API 래퍼 구현
- [ ] 예치금 계좌 모델 생성 (`DepositAccount`, `DepositTransaction`)
- [ ] 실제 매수/매도 로직 구현
- [ ] 예치금 입금/출금 시스템
- [ ] 포지션 동기화 로직
- [ ] Paper Trading 테스트
- [ ] Live Trading 전환

### **Phase 3: 개선 & 확장 (2-3주)**
- [ ] 알림 시스템 (수익 달성, 매도 가능 등)
- [ ] 대시보드 개선
- [ ] 사용자 피드백 반영

**총 예상 기간: 8-12주 (2-3개월)**

---

## 💳 **예치금 입출금 시스템**

### **3-1. 은행 계좌 연동: Plaid API** ✅

**Plaid API 선택 이유:**
- ✅ 미국 은행 계좌 연동 표준
- ✅ ACH 전송 지원 (Payment Initiation 제품)
- ✅ Sandbox 환경으로 무료 테스트 가능
- ✅ 대부분의 미국 은행 지원
- ✅ API 문서 및 SDK 풍부

**설정 가이드**: `docs/ALPACA_PLAID_SETUP.md` 참고

**비용:**
- Sandbox: 무료
- Development: 무료 (제한적)
- Production: 사용량 기반 (월 $0.25 ~ $2.50 per account)

### **3-2. 예치금 입출금 플로우**

```
입금:
1. 사용자: "예치금 계좌에 $100 입금" 요청
2. 시스템: Plaid로 은행 계좌 인증
3. 시스템: ACH 전송으로 $100 입금
4. 시스템: DepositAccount.balance += $100
5. 시스템: DepositTransaction 기록

출금:
1. 사용자: "예치금 $50 출금" 요청
2. 시스템: 잔액 확인
3. 시스템: ACH 전송으로 $50 출금
4. 시스템: DepositAccount.balance -= $50
5. 시스템: DepositTransaction 기록
```

---

## 🎯 **다음 액션 (시뮬레이션 우선)**

### **Phase 1: 시뮬레이션 MVP + 은행 연동 (즉시 시작)**

**목표**: 실제 계좌 연동 포함한 전체 플로우 구현

1. [ ] 데이터 모델 생성
   - `CategoryAccount` (카테고리별 통장) - 은행 연동 필드 추가
   - `UserBankAccount` (은행 계좌)
   - `Transaction` (입금/출금 내역) - Plaid 연동 필드 추가
   - `SavingsReward` (절약 → 투자)

2. [ ] 마이그레이션 생성 및 적용

3. [ ] Plaid 연동 (기본)
   - Plaid Link Token 생성 API
   - Public Token 교환 API
   - 계좌 정보 조회
   - `UserBankAccount` 생성

4. [ ] API 엔드포인트 구현
   - 통장 관리 (생성, 입금, 출금)
   - 은행 계좌 연동 (`link_bank_account`)
   - 절약 계산
   - 투자 생성 (시뮬레이션)
   - 매도 처리 (시뮬레이션)

5. [ ] 프론트엔드 UI
   - 홈 화면 (오늘 아낀 돈, 투자 현황)
   - 은행 계좌 연결 (Plaid Link)
   - 통장 관리 (은행 연동 설정)
   - 투자 상세

6. [ ] 주가 업데이트 스케줄러 (Celery)
   - StockPrice 테이블 사용
   - 매일 자동 업데이트

7. [ ] 전체 플로우 테스트

**참고**: 
- 전체 플로우: `docs/SERVICE_FLOW.md`
- 은행 연동 상세: `docs/BANK_ACCOUNT_INTEGRATION.md`

### **Phase 2: 실제 계좌 연동 (추후)**

1. [ ] Alpaca API 계정 생성 및 연동
2. [ ] Plaid API 계정 생성 및 연동
3. [ ] 예치금 시스템 구현
4. [ ] 실제 매매 로직 구현

---

**작성자**: AI Assistant  
**검토 필요**: 데이터 모델, API 설계, 법적 리스크

