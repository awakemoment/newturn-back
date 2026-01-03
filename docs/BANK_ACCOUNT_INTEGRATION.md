# 💳 카테고리별 통장 - 실제 은행 계좌 연동 가이드

**작성일**: 2024.11.07  
**목적**: Plaid를 통한 카테고리별 통장과 실제 은행 계좌 연동

---

## 🎯 **연동 개념**

### **핵심 아이디어:**
- 사용자가 실제 은행 계좌를 Plaid로 연결
- 카테고리별 통장을 실제 은행 계좌와 연동
- 입금/출금 시 실제 은행 계좌와 동기화
- 자동 소비 추적 (Plaid Transactions API)

---

## 📊 **데이터 모델**

### **1. UserBankAccount (사용자 은행 계좌)**

```python
# apps/accounts/models.py

class UserBankAccount(models.Model):
    """사용자 은행 계좌 (Plaid 연동)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_accounts')
    
    # Plaid 정보
    plaid_access_token = models.CharField(max_length=200)  # 암호화 필요
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_bank_accounts'
        unique_together = ['user', 'plaid_account_id']
    
    def __str__(self):
        return f"{self.user.username} - {self.bank_name} {self.account_name}"
```

### **2. CategoryAccount 업데이트**

```python
class CategoryAccount(models.Model):
    # ... 기존 필드들 ...
    
    # 실제 은행 계좌 연동
    linked_bank_account = models.ForeignKey(
        'UserBankAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='category_accounts',
        verbose_name='연동된 은행 계좌'
    )
    auto_sync_enabled = models.BooleanField(default=False)  # 자동 동기화 활성화 여부
    sync_category_rules = models.JSONField(default=dict, blank=True)  # 카테고리 매핑 규칙
    # 예: {"merchant_name_contains": ["starbucks", "coffee"], "category": "coffee"}
```

---

## 🔄 **연동 플로우**

### **1. 은행 계좌 연결**

```
사용자: "은행 계좌 연결" 클릭
  ↓
백엔드: Plaid Link Token 생성
  POST /api/plaid/link-token/
  → link_token 반환
  ↓
프론트엔드: Plaid Link 열기
  - 사용자가 은행 선택
  - 로그인
  - 계좌 선택
  ↓
프론트엔드: Public Token 받음
  ↓
백엔드: Public Token → Access Token 교환
  POST /api/plaid/exchange-token/
  → access_token 저장
  → UserBankAccount 생성
  ↓
백엔드: 계좌 정보 조회
  → 계좌명, 잔액 등 저장
```

### **2. 카테고리 통장과 연동**

```
사용자: "카페/베이커리 통장" 설정
  ↓
은행 계좌 선택
  - 연결된 은행 계좌 목록 표시
  - "Chase Checking" 선택
  ↓
자동 동기화 설정
  - "자동 동기화 활성화" 체크
  - 카테고리 매핑 규칙 설정
    * merchant_name에 "starbucks", "coffee" 포함 → coffee 카테고리
    * merchant_name에 "bakery", "donut" 포함 → bakery 카테고리
  ↓
CategoryAccount 업데이트
  - linked_bank_account 설정
  - auto_sync_enabled = True
  - sync_category_rules 저장
```

### **3. 자동 소비 추적**

```
매일 자동 실행 (Celery)
  ↓
Plaid Transactions API 호출
  - 최근 30일 거래 내역 조회
  - 카테고리별로 필터링
  ↓
카테고리 매핑
  - merchant_name, category로 매칭
  - 해당 CategoryAccount 찾기
  ↓
Transaction 생성
  - type: 'bank_sync'
  - is_synced_from_bank: True
  - plaid_transaction_id 저장
  ↓
CategoryAccount 업데이트
  - current_month_spent 증가
  - balance 감소 (출금인 경우)
```

### **4. 수동 입금/출금 (실제 계좌 연동)**

```
입금:
사용자: "카페/베이커리 통장에 $100 입금"
  ↓
연동된 은행 계좌 확인
  - linked_bank_account 존재?
  - auto_sync_enabled = True?
  ↓
Plaid ACH 전송 (또는 수동 처리)
  - 실제 은행 계좌에서 $100 출금
  - 카테고리 통장에 $100 입금
  ↓
Transaction 생성
  - type: 'deposit'
  - bank_transaction_id 저장
  ↓
CategoryAccount 업데이트
  - balance += $100
  - total_deposited += $100

출금:
사용자: "커피 $5 구매" 기록
  ↓
연동된 은행 계좌 확인
  ↓
실제 은행 계좌에서 $5 출금 (선택사항)
  - 또는 자동 동기화로 추적만
  ↓
Transaction 생성
  - type: 'withdrawal'
  - merchant_name: "Starbucks"
  ↓
CategoryAccount 업데이트
  - balance -= $5
  - current_month_spent += $5
```

---

## 🔧 **구현 코드**

### **1. Plaid API 서비스**

```python
# apps/accounts/services/plaid_service.py

from apps.broker.plaid_api import PlaidAPI
from apps.accounts.models import UserBankAccount, CategoryAccount, Transaction
from decimal import Decimal
from django.utils import timezone

class PlaidIntegrationService:
    """Plaid 연동 서비스"""
    
    def __init__(self):
        self.plaid = PlaidAPI()
    
    def sync_bank_transactions(self, user_bank_account: UserBankAccount):
        """
        은행 거래 내역 동기화
        
        Args:
            user_bank_account: UserBankAccount 객체
        """
        # Plaid Transactions API로 최근 거래 조회
        transactions = self.plaid.get_transactions(
            access_token=user_bank_account.plaid_access_token,
            start_date=(timezone.now() - timedelta(days=30)).date(),
            end_date=timezone.now().date()
        )
        
        # 연동된 카테고리 통장들 찾기
        category_accounts = CategoryAccount.objects.filter(
            linked_bank_account=user_bank_account,
            auto_sync_enabled=True
        )
        
        for plaid_txn in transactions:
            # 이미 동기화된 거래인지 확인
            existing = Transaction.objects.filter(
                plaid_transaction_id=plaid_txn['transaction_id']
            ).first()
            
            if existing:
                continue  # 이미 동기화됨
            
            # 카테고리 매핑
            category_account = self._match_category(
                plaid_txn,
                category_accounts
            )
            
            if not category_account:
                continue  # 매칭되는 카테고리 없음
            
            # Transaction 생성
            amount = Decimal(str(abs(plaid_txn['amount'])))
            is_debit = plaid_txn['amount'] < 0  # 출금인 경우
            
            Transaction.objects.create(
                account=category_account,
                transaction_type='bank_sync' if is_debit else 'deposit',
                amount=amount,
                balance_after=category_account.balance - amount if is_debit else category_account.balance + amount,
                merchant_name=plaid_txn.get('merchant_name', ''),
                category_detail=plaid_txn.get('category', []),
                plaid_transaction_id=plaid_txn['transaction_id'],
                bank_transaction_id=plaid_txn.get('authorized_date', ''),
                is_synced_from_bank=True,
                bank_transaction_date=plaid_txn.get('date'),
                note=f"자동 동기화: {plaid_txn.get('name', '')}"
            )
            
            # CategoryAccount 업데이트
            if is_debit:
                category_account.balance -= amount
                category_account.current_month_spent += amount
            else:
                category_account.balance += amount
                category_account.total_deposited += amount
            
            category_account.save()
        
        # 마지막 동기화 시간 업데이트
        user_bank_account.last_synced_at = timezone.now()
        user_bank_account.save()
    
    def _match_category(self, plaid_transaction, category_accounts):
        """
        Plaid 거래를 카테고리 통장에 매칭
        
        Args:
            plaid_transaction: Plaid 거래 데이터
            category_accounts: CategoryAccount 쿼리셋
        
        Returns:
            매칭된 CategoryAccount 또는 None
        """
        merchant_name = plaid_transaction.get('merchant_name', '').lower()
        transaction_name = plaid_transaction.get('name', '').lower()
        categories = plaid_transaction.get('category', [])
        
        for account in category_accounts:
            rules = account.sync_category_rules or {}
            
            # merchant_name 매칭
            if 'merchant_name_contains' in rules:
                keywords = rules['merchant_name_contains']
                if any(keyword.lower() in merchant_name or keyword.lower() in transaction_name 
                       for keyword in keywords):
                    return account
            
            # category 매칭
            if 'category' in rules:
                if rules['category'] in categories:
                    return account
        
        return None
    
    def transfer_to_category_account(
        self,
        user_bank_account: UserBankAccount,
        category_account: CategoryAccount,
        amount: Decimal
    ):
        """
        실제 은행 계좌에서 카테고리 통장으로 입금 (ACH 전송)
        
        참고: Plaid Payment Initiation 제품 필요
        """
        # Plaid ACH 전송 (또는 수동 처리)
        # 실제 구현은 Payment Initiation API 사용
        
        # Transaction 생성
        category_account.balance += amount
        category_account.total_deposited += amount
        category_account.save()
        
        Transaction.objects.create(
            account=category_account,
            transaction_type='deposit',
            amount=amount,
            balance_after=category_account.balance,
            note=f"은행 계좌에서 입금: {user_bank_account.bank_name}"
        )
        
        return category_account
```

### **2. Plaid API 확장**

```python
# apps/broker/plaid_api.py (추가 메서드)

def get_transactions(self, access_token: str, start_date: date, end_date: date) -> list:
    """
    거래 내역 조회
    
    Args:
        access_token: Plaid Access Token
        start_date: 시작일
        end_date: 종료일
    
    Returns:
        거래 내역 리스트
    """
    from plaid.model.transactions_get_request import TransactionsGetRequest
    from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
    
    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date,
        options=TransactionsGetRequestOptions(
            count=500,  # 최대 500개
            offset=0
        )
    )
    
    response = self.client.transactions_get(request)
    
    return [
        {
            'transaction_id': txn['transaction_id'],
            'name': txn['name'],
            'merchant_name': txn.get('merchant_name'),
            'amount': txn['amount'],
            'date': txn['date'],
            'authorized_date': txn.get('authorized_date'),
            'category': txn.get('category', []),
        }
        for txn in response['transactions']
    ]
```

---

## 📱 **API 엔드포인트**

### **1. Plaid Link Token 생성**

```python
# api/plaid/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.accounts.services.plaid_service import PlaidIntegrationService

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_link_token(request):
    """Plaid Link Token 생성"""
    service = PlaidIntegrationService()
    link_token = service.plaid.create_link_token(str(request.user.id))
    
    return Response({'link_token': link_token})
```

### **2. Public Token 교환**

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def exchange_public_token(request):
    """Public Token을 Access Token으로 교환"""
    public_token = request.data.get('public_token')
    
    if not public_token:
        return Response({'error': 'public_token이 필요합니다.'}, status=400)
    
    service = PlaidIntegrationService()
    access_token = service.plaid.exchange_public_token(public_token)
    
    # 계좌 정보 조회
    accounts = service.plaid.get_accounts(access_token)
    
    # UserBankAccount 생성
    for acc in accounts:
        UserBankAccount.objects.create(
            user=request.user,
            plaid_access_token=access_token,  # 암호화 필요!
            plaid_item_id=acc.get('item_id'),
            plaid_account_id=acc['account_id'],
            bank_name=acc.get('institution_name', ''),
            account_name=acc['name'],
            account_type=acc['type'],
            account_number_masked=acc.get('mask', ''),
            current_balance=acc['balance'],
            available_balance=acc['balance'],
        )
    
    return Response({'success': True, 'accounts': accounts})
```

### **3. 카테고리 통장 연동**

```python
# api/accounts/views.py

@action(detail=True, methods=['post'])
def link_bank_account(self, request, pk=None):
    """카테고리 통장에 은행 계좌 연동"""
    account = self.get_object()
    bank_account_id = request.data.get('bank_account_id')
    auto_sync = request.data.get('auto_sync_enabled', False)
    sync_rules = request.data.get('sync_category_rules', {})
    
    try:
        bank_account = UserBankAccount.objects.get(
            id=bank_account_id,
            user=request.user
        )
        
        account.linked_bank_account = bank_account
        account.auto_sync_enabled = auto_sync
        account.sync_category_rules = sync_rules
        account.save()
        
        return Response(CategoryAccountSerializer(account).data)
    except UserBankAccount.DoesNotExist:
        return Response(
            {'error': '은행 계좌를 찾을 수 없습니다.'},
            status=404
        )
```

### **4. 거래 동기화**

```python
@action(detail=False, methods=['post'])
def sync_bank_transactions(self, request):
    """은행 거래 내역 동기화"""
    bank_account_id = request.data.get('bank_account_id')
    
    try:
        bank_account = UserBankAccount.objects.get(
            id=bank_account_id,
            user=request.user
        )
        
        service = PlaidIntegrationService()
        service.sync_bank_transactions(bank_account)
        
        return Response({'success': True})
    except UserBankAccount.DoesNotExist:
        return Response(
            {'error': '은행 계좌를 찾을 수 없습니다.'},
            status=404
        )
```

---

## ⚙️ **자동 동기화 스케줄러**

```python
# apps/accounts/tasks.py

from celery import shared_task
from apps.accounts.models import UserBankAccount
from apps.accounts.services.plaid_service import PlaidIntegrationService

@shared_task
def sync_all_bank_transactions():
    """모든 연동된 은행 계좌의 거래 내역 동기화"""
    service = PlaidIntegrationService()
    
    bank_accounts = UserBankAccount.objects.filter(
        is_active=True
    )
    
    for bank_account in bank_accounts:
        try:
            service.sync_bank_transactions(bank_account)
        except Exception as e:
            # 에러 로깅
            print(f"동기화 실패: {bank_account.id} - {str(e)}")
    
    return "Bank transactions synced"
```

**Celery Beat 설정:**
```python
# config/celery.py

from celery.schedules import crontab

app.conf.beat_schedule = {
    'sync-bank-transactions': {
        'task': 'apps.accounts.tasks.sync_all_bank_transactions',
        'schedule': crontab(hour=2, minute=0),  # 매일 새벽 2시
    },
}
```

---

## 🎨 **UI/UX 플로우**

### **은행 계좌 연결 화면**

```
┌─────────────────────────────────────┐
│  은행 계좌 연결                     │
│                                     │
│  [Plaid Link 버튼]                 │
│  "은행 계좌를 연결하여 자동으로    │
│   소비를 추적하세요"                │
└─────────────────────────────────────┘
```

### **카테고리 통장 연동 설정**

```
┌─────────────────────────────────────┐
│  카페/베이커리 통장 설정            │
│                                     │
│  연동된 은행 계좌:                  │
│  [Chase Checking ****1234] ▼       │
│                                     │
│  ☑️ 자동 동기화 활성화              │
│                                     │
│  카테고리 매핑 규칙:                │
│  • merchant_name에 포함:            │
│    [starbucks] [coffee] [cafe]     │
│  • category:                        │
│    [Food and Drink]                │
│                                     │
│  [저장]                             │
└─────────────────────────────────────┘
```

---

## 🔒 **보안 고려사항**

### **1. Access Token 암호화**

```python
# apps/accounts/utils/encryption.py

from cryptography.fernet import Fernet
from django.conf import settings
import base64

def encrypt_access_token(token: str) -> str:
    """Plaid Access Token 암호화"""
    key = settings.PLAID_ENCRYPTION_KEY
    f = Fernet(key)
    return f.encrypt(token.encode()).decode()

def decrypt_access_token(encrypted_token: str) -> str:
    """Plaid Access Token 복호화"""
    key = settings.PLAID_ENCRYPTION_KEY
    f = Fernet(key)
    return f.decrypt(encrypted_token.encode()).decode()
```

### **2. 모델에 암호화 적용**

```python
class UserBankAccount(models.Model):
    _plaid_access_token = models.TextField(db_column='plaid_access_token')
    
    @property
    def plaid_access_token(self):
        return decrypt_access_token(self._plaid_access_token)
    
    @plaid_access_token.setter
    def plaid_access_token(self, value):
        self._plaid_access_token = encrypt_access_token(value)
```

---

## 📋 **구현 체크리스트**

### **Phase 1: 기본 연동 (1주)**
- [ ] `UserBankAccount` 모델 생성
- [ ] `CategoryAccount`에 `linked_bank_account` 필드 추가
- [ ] Plaid Link Token 생성 API
- [ ] Public Token 교환 API
- [ ] 프론트엔드 Plaid Link 연동

### **Phase 2: 자동 동기화 (1주)**
- [ ] Plaid Transactions API 연동
- [ ] 카테고리 매핑 로직
- [ ] 자동 동기화 스케줄러
- [ ] 거래 내역 동기화 API

### **Phase 3: ACH 전송 (2주)**
- [ ] Plaid Payment Initiation 설정
- [ ] ACH 전송 로직
- [ ] 입금/출금 연동

---

**작성자**: AI Assistant  
**업데이트**: 2024.11.07

