# 🔧 Alpaca & Plaid 설정 가이드

**작성일**: 2024.11.07  
**목적**: Alpaca (주식 매매) + Plaid (은행 계좌 연동) 설정 및 구현 가이드

---

## 📋 **1. Alpaca API 설정**

### **1-1. 계정 생성**

1. **Alpaca 가입**: https://alpaca.markets/
2. **Paper Trading 계정 생성** (테스트용)
   - Dashboard → Paper Trading 활성화
   - 무료로 가상 자금 $100,000 제공
3. **API 키 발급**
   - Dashboard → API Keys → Generate New Key
   - `API Key ID`와 `Secret Key` 복사

### **1-2. 환경변수 설정**

```bash
# .env 파일
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_PAPER=True  # Paper Trading 모드 (True) 또는 Live Trading (False)
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # Paper Trading URL
```

### **1-3. 패키지 설치**

```bash
pip install alpaca-py
```

### **1-4. 기본 사용법**

```python
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient

# Trading Client (매수/매도)
trading_client = TradingClient(
    api_key=os.getenv('ALPACA_API_KEY'),
    secret_key=os.getenv('ALPACA_SECRET_KEY'),
    paper=True  # Paper Trading
)

# Data Client (주가 조회)
data_client = StockHistoricalDataClient(
    api_key=os.getenv('ALPACA_API_KEY'),
    secret_key=os.getenv('ALPACA_SECRET_KEY')
)
```

---

## 💳 **2. Plaid API 설정**

### **2-1. 계정 생성**

1. **Plaid 가입**: https://dashboard.plaid.com/signup
2. **Sandbox 환경 사용** (테스트용)
   - 무료 플랜으로 시작 가능
   - Sandbox 모드에서 테스트
3. **API 키 발급**
   - Dashboard → Team Settings → Keys
   - `client_id`와 `secret` 복사

### **2-2. 환경변수 설정**

```bash
# .env 파일
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_secret_here
PLAID_ENV=sandbox  # sandbox, development, production
PLAID_PRODUCTS=transactions,auth  # 사용할 제품 (transactions, auth, identity 등)
```

### **2-3. 패키지 설치**

```bash
pip install plaid-python
```

### **2-4. 기본 사용법**

```python
from plaid.api import plaid_api
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.configuration import Configuration
from plaid.api_client import ApiClient

# Plaid 설정
configuration = Configuration(
    host=plaid.Environment.sandbox,  # sandbox, development, production
    api_key={
        'clientId': os.getenv('PLAID_CLIENT_ID'),
        'secret': os.getenv('PLAID_SECRET'),
    }
)

api_client = ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
```

---

## 🔗 **3. 통합 구현**

### **3-1. Alpaca API 래퍼 (완성본)**

```python
# apps/broker/alpaca_api.py

import os
from decimal import Decimal
from typing import Optional
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from django.conf import settings

class AlpacaAPI:
    """Alpaca API 래퍼"""
    
    def __init__(self, paper: Optional[bool] = None):
        """
        Alpaca API 초기화
        
        Args:
            paper: Paper Trading 모드 (None이면 환경변수에서 가져옴)
        """
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY')
        self.paper = paper if paper is not None else os.getenv('ALPACA_PAPER', 'True') == 'True'
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API 키가 설정되지 않았습니다.")
        
        # Trading Client (매수/매도)
        self.trading_client = TradingClient(
            api_key=self.api_key,
            secret_key=self.secret_key,
            paper=self.paper
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
                quote = latest_quote[symbol]
                # Bid와 Ask의 중간가 사용
                bid = Decimal(str(quote.bid_price))
                ask = Decimal(str(quote.ask_price))
                return (bid + ask) / 2
            else:
                raise ValueError(f"주가 데이터를 찾을 수 없습니다: {symbol}")
        except Exception as e:
            raise ValueError(f"주가 조회 실패: {str(e)}")
    
    def buy_stock(self, symbol: str, quantity: int, order_type: str = 'market') -> dict:
        """
        주식 매수
        
        Args:
            symbol: 종목 코드 (예: 'AAPL', 'NVDA')
            quantity: 매수 주수 (정수)
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
            if quantity <= 0:
                raise ValueError("매수 주수는 1주 이상이어야 합니다.")
            
            if order_type == 'market':
                order_request = MarketOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                )
            else:
                # Limit order는 가격 필요
                current_price = self.get_current_price(symbol)
                order_request = LimitOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY,
                    limit_price=float(current_price)
                )
            
            order = self.trading_client.submit_order(order_request)
            
            return {
                'order_id': str(order.id),
                'status': order.status.value,
                'filled_qty': Decimal(str(order.filled_qty or 0)),
                'filled_avg_price': Decimal(str(order.filled_avg_price or 0)),
                'commission': Decimal('0')  # Alpaca는 커미션 무료
            }
        except Exception as e:
            raise ValueError(f"매수 주문 실패: {str(e)}")
    
    def sell_stock(self, symbol: str, quantity: int, order_type: str = 'market') -> dict:
        """주식 매도"""
        try:
            if quantity <= 0:
                raise ValueError("매도 주수는 1주 이상이어야 합니다.")
            
            if order_type == 'market':
                order_request = MarketOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                )
            else:
                current_price = self.get_current_price(symbol)
                order_request = LimitOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY,
                    limit_price=float(current_price)
                )
            
            order = self.trading_client.submit_order(order_request)
            
            return {
                'order_id': str(order.id),
                'status': order.status.value,
                'filled_qty': Decimal(str(order.filled_qty or 0)),
                'filled_avg_price': Decimal(str(order.filled_avg_price or 0)),
                'commission': Decimal('0')
            }
        except Exception as e:
            raise ValueError(f"매도 주문 실패: {str(e)}")
    
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

### **3-2. Plaid API 래퍼**

```python
# apps/broker/plaid_api.py

import os
from decimal import Decimal
from typing import Optional, Dict
from plaid.api import plaid_api
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.auth_get_request import AuthGetRequest
from plaid.model.payment_initiation.payment_create_request import PaymentCreateRequest
from plaid.model.payment_initiation.recipient_create_request import RecipientCreateRequest
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid import ApiException

class PlaidAPI:
    """Plaid API 래퍼"""
    
    def __init__(self):
        """Plaid API 초기화"""
        self.client_id = os.getenv('PLAID_CLIENT_ID')
        self.secret = os.getenv('PLAID_SECRET')
        self.env = os.getenv('PLAID_ENV', 'sandbox')
        
        if not self.client_id or not self.secret:
            raise ValueError("Plaid API 키가 설정되지 않았습니다.")
        
        # 환경 설정
        environments = {
            'sandbox': plaid.Environment.sandbox,
            'development': plaid.Environment.development,
            'production': plaid.Environment.production,
        }
        
        configuration = Configuration(
            host=environments.get(self.env, plaid.Environment.sandbox),
            api_key={
                'clientId': self.client_id,
                'secret': self.secret,
            }
        )
        
        api_client = ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)
    
    def create_link_token(self, user_id: str) -> str:
        """
        Link Token 생성 (은행 계좌 연결용)
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            link_token: 프론트엔드에서 사용할 Link Token
        """
        from plaid.model.link_token_create_request import LinkTokenCreateRequest
        from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
        
        request = LinkTokenCreateRequest(
            products=[Products('auth'), Products('transactions')],
            client_name='Newturn',
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id=user_id
            )
        )
        
        response = self.client.link_token_create(request)
        return response['link_token']
    
    def exchange_public_token(self, public_token: str) -> str:
        """
        Public Token을 Access Token으로 교환
        
        Args:
            public_token: Plaid Link에서 받은 public_token
        
        Returns:
            access_token: 계좌 접근용 토큰
        """
        request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        
        response = self.client.item_public_token_exchange(request)
        return response['access_token']
    
    def get_accounts(self, access_token: str) -> list:
        """
        연결된 계좌 목록 조회
        
        Args:
            access_token: Plaid Access Token
        
        Returns:
            계좌 목록
        """
        request = AccountsGetRequest(access_token=access_token)
        response = self.client.accounts_get(request)
        
        return [
            {
                'account_id': acc['account_id'],
                'name': acc['name'],
                'type': acc['type'],
                'subtype': acc.get('subtype'),
                'balance': Decimal(str(acc['balances']['available'] or 0)),
            }
            for acc in response['accounts']
        ]
    
    def get_account_balance(self, access_token: str, account_id: str) -> Decimal:
        """
        특정 계좌 잔액 조회
        
        Args:
            access_token: Plaid Access Token
            account_id: 계좌 ID
        
        Returns:
            잔액
        """
        accounts = self.get_accounts(access_token)
        account = next((acc for acc in accounts if acc['account_id'] == account_id), None)
        
        if not account:
            raise ValueError(f"계좌를 찾을 수 없습니다: {account_id}")
        
        return account['balance']
    
    def initiate_ach_transfer(self, access_token: str, account_id: str, amount: Decimal, description: str) -> dict:
        """
        ACH 전송 시작 (입금/출금)
        
        참고: Plaid의 Payment Initiation은 별도 제품이 필요할 수 있습니다.
        초기에는 수동 처리 또는 다른 방법 사용 권장.
        
        Args:
            access_token: Plaid Access Token
            account_id: 계좌 ID
            amount: 전송 금액
            description: 설명
        
        Returns:
            전송 결과
        """
        # Payment Initiation은 별도 설정 필요
        # 초기에는 수동 처리 또는 Stripe ACH 사용 권장
        raise NotImplementedError("ACH 전송은 Payment Initiation 제품이 필요합니다.")
```

---

## 🔄 **4. 통합 플로우**

### **4-1. 예치금 입금 플로우**

```
1. 사용자: "예치금 $100 입금" 요청
2. 프론트엔드: Plaid Link 열기
3. 사용자: 은행 계좌 연결
4. 백엔드: Public Token → Access Token 교환
5. 백엔드: 계좌 정보 저장 (UserBankAccount 모델)
6. 사용자: 입금 금액 입력 ($100)
7. 백엔드: ACH 전송 요청 (또는 수동 처리)
8. 백엔드: DepositAccount.balance += $100
9. 백엔드: DepositTransaction 기록
```

### **4-2. 주식 매수 플로우**

```
1. 사용자: "절약 금액 $20으로 NVDA 매수" 요청
2. 백엔드: 예치금 잔액 확인
3. 백엔드: Alpaca API로 NVDA 현재가 조회
4. 백엔드: 매수 가능 주수 계산 (정수)
5. 백엔드: Alpaca API로 매수 주문
6. 백엔드: 예치금 차감
7. 백엔드: SavingsReward 생성
8. 백엔드: DepositTransaction 기록
```

### **4-3. 주식 매도 플로우**

```
1. 사용자: "NVDA 매도" 요청
2. 백엔드: SavingsReward 조회
3. 백엔드: 수익 여부 확인 (can_sell)
4. 백엔드: Alpaca API로 매도 주문
5. 백엔드: 예치금 입금
6. 백엔드: SavingsReward 업데이트
7. 백엔드: DepositTransaction 기록
```

---

## 📝 **5. 데이터 모델 확장**

```python
# apps/accounts/models.py (추가)

class UserBankAccount(models.Model):
    """사용자 은행 계좌 (Plaid 연동)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_accounts')
    
    # Plaid 정보
    plaid_access_token = models.CharField(max_length=200)  # 암호화 필요
    plaid_item_id = models.CharField(max_length=100)
    plaid_account_id = models.CharField(max_length=100)
    
    # 계좌 정보
    bank_name = models.CharField(max_length=200)
    account_name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=50)  # checking, savings
    account_number_masked = models.CharField(max_length=20)  # 마스킹된 계좌번호
    
    # 상태
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_bank_accounts'
        unique_together = ['user', 'plaid_account_id']
```

---

## 🚀 **6. 다음 단계**

### **즉시 시작:**
1. [ ] Alpaca 계정 생성 및 API 키 발급
2. [ ] Plaid 계정 생성 및 API 키 발급
3. [ ] 환경변수 설정 (.env)
4. [ ] 패키지 설치 (`pip install -r requirements_alpaca.txt`)

### **이번 주:**
1. [ ] Alpaca API 래퍼 구현 및 테스트
2. [ ] Plaid API 래퍼 구현 및 테스트
3. [ ] Paper Trading으로 매수/매도 테스트

### **다음 주:**
1. [ ] 예치금 시스템과 통합
2. [ ] 프론트엔드 Plaid Link 연동
3. [ ] 전체 플로우 테스트

---

## 📊 **7. Alpaca API 기능 확인**

**✅ 구현 가능한 기능:**
- 주식 매수/매도 (시장가, 지정가)
- 보유 종목 조회 (실시간 포지션, 수익/손실)
- 계좌 정보 조회 (잔액, 총 자산, 구매력)
- 주문 내역 조회 및 취소
- 주가 조회 (실시간, 과거 데이터)

**상세 내용**: `docs/ALPACA_FEATURES.md` 참고

---

## ⚠️ **주의사항**

### **Alpaca:**
- Paper Trading과 Live Trading은 별도 계좌
- Live Trading 전환 시 충분한 테스트 필요
- API Rate Limit 확인 (초당 요청 수 제한)

### **Plaid:**
- Sandbox 환경에서는 테스트 계좌만 사용 가능
- Production 전환 시 Plaid 승인 필요
- ACH 전송은 Payment Initiation 제품 필요 (별도 비용)

### **보안:**
- API 키는 절대 코드에 하드코딩하지 않기
- Plaid Access Token은 암호화하여 저장
- 환경변수는 `.env` 파일로 관리 (Git에 커밋 금지)

---

**작성자**: AI Assistant  
**업데이트**: 2024.11.07

