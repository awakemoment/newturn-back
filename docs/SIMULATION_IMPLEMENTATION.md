# 🎮 시뮬레이션 모드 구현 가이드

**작성일**: 2024.11.07  
**목적**: Alpaca/Plaid API 인터페이스를 참고한 시뮬레이션 구현 및 실제 API 전환 방법

---

## 🎯 **핵심 설계 원칙**

### **1. 인터페이스 기반 설계**
- `BrokerAPIInterface`: 주식 매매 API 인터페이스
- `BankAPIInterface`: 은행 계좌 API 인터페이스
- 시뮬레이션과 실제 API가 동일한 인터페이스 구현

### **2. 팩토리 패턴**
- 환경변수로 시뮬레이션/실제 API 선택
- 코드 변경 없이 전환 가능

### **3. 추상화 레이어**
- 서비스 레이어에서 인터페이스만 사용
- 구현체 변경이 서비스 로직에 영향 없음

---

## 📁 **파일 구조**

```
apps/broker/
├── __init__.py
├── interfaces.py          # 인터페이스 정의
├── simulation.py          # 시뮬레이션 구현
├── alpaca_api.py          # 실제 Alpaca 구현
├── plaid_api.py           # 실제 Plaid 구현
└── factory.py             # 팩토리 (인스턴스 생성)

apps/accounts/services/
├── trading_service.py     # 투자 서비스 (브로커 API 사용)
└── plaid_service.py       # Plaid 연동 서비스 (은행 API 사용)
```

---

## 🔧 **사용 방법**

### **1. 환경변수 설정**

```bash
# .env 파일

# 시뮬레이션 모드 (기본)
USE_SIMULATION_BROKER=True
USE_SIMULATION_BANK=True

# 실제 API 모드로 전환 시
USE_SIMULATION_BROKER=False
USE_SIMULATION_BANK=False
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret
ALPACA_PAPER=True
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_secret
PLAID_ENV=sandbox
```

### **2. 코드에서 사용**

```python
# 서비스 레이어에서 사용
from apps.broker.factory import get_broker_api, get_bank_api

# 브로커 API (자동으로 시뮬레이션/실제 선택)
broker = get_broker_api(deposit_account=deposit_account)
current_price = broker.get_current_price('NVDA')
order = broker.buy_stock('NVDA', 1, 'market')

# 은행 API (자동으로 시뮬레이션/실제 선택)
bank = get_bank_api()
link_token = bank.create_link_token(user_id='123')
accounts = bank.get_accounts(access_token)
```

### **3. 강제로 시뮬레이션 사용**

```python
# 테스트 등에서 강제로 시뮬레이션 사용
broker = get_broker_api(deposit_account=deposit_account, force_simulation=True)
bank = get_bank_api(force_simulation=True)
```

---

## 🔄 **시뮬레이션 → 실제 API 전환**

### **전환 방법:**

**1. 환경변수만 변경:**
```bash
# .env 파일 수정
USE_SIMULATION_BROKER=False
USE_SIMULATION_BANK=False

# Alpaca/Plaid API 키 설정
ALPACA_API_KEY=...
PLAID_CLIENT_ID=...
```

**2. 코드 변경 없음!**
- 서비스 레이어 코드는 그대로
- 팩토리가 자동으로 실제 API 인스턴스 반환

---

## 📊 **시뮬레이션 모드 동작**

### **1. 주식 매매 (SimulationBrokerAPI)**

**데이터 소스:**
- 주가: `StockPrice` 테이블 (최신 close_price 사용)
- 포지션: 메모리 저장 (실제로는 DB에 저장 가능)
- 주문: 메모리 저장 (실제로는 DB에 저장 가능)

**특징:**
- 즉시 체결 (지연 없음)
- 수수료 $0
- 예치금 자동 차감/입금

### **2. 은행 연동 (SimulationBankAPI)**

**데이터 소스:**
- 계좌: 메모리 저장 (시뮬레이션 계좌)
- 거래 내역: 메모리 저장 (예시 거래)

**특징:**
- Link Token 즉시 생성
- Public Token → Access Token 즉시 교환
- 샘플 거래 내역 제공

---

## 🎨 **실제 사용 예시**

### **예시 1: 주식 매수**

```python
from apps.accounts.services.trading_service import TradingService
from apps.accounts.models import DepositAccount, SavingsReward

# 예치금 계좌
deposit_account = DepositAccount.objects.get(user=user)

# 투자 서비스 생성 (자동으로 시뮬레이션/실제 선택)
service = TradingService(deposit_account=deposit_account)

# 절약 리워드로 투자
reward = SavingsReward.objects.get(id=reward_id)
service.execute_investment(reward)

# 시뮬레이션 모드: StockPrice 테이블 사용, 즉시 체결
# 실제 모드: Alpaca API 호출, 실제 매수
```

### **예시 2: 은행 거래 동기화**

```python
from apps.accounts.services.plaid_service import PlaidIntegrationService
from apps.accounts.models import UserBankAccount

# Plaid 연동 서비스 생성 (자동으로 시뮬레이션/실제 선택)
service = PlaidIntegrationService()

# 은행 계좌
bank_account = UserBankAccount.objects.get(user=user)

# 거래 내역 동기화
service.sync_bank_transactions(bank_account)

# 시뮬레이션 모드: 메모리에서 샘플 거래 조회
# 실제 모드: Plaid Transactions API 호출
```

---

## 🧪 **테스트**

### **시뮬레이션 모드 테스트**

```python
# tests/test_trading_service.py

from django.test import TestCase
from apps.accounts.services.trading_service import TradingService
from apps.broker.factory import get_broker_api

class TradingServiceTest(TestCase):
    def setUp(self):
        # 시뮬레이션 모드 강제
        self.broker = get_broker_api(force_simulation=True)
    
    def test_buy_stock(self):
        # 주식 매수 테스트
        order = self.broker.buy_stock('NVDA', 1, 'market')
        self.assertEqual(order['status'], 'filled')
        self.assertEqual(order['filled_qty'], 1)
```

---

## 📋 **구현 체크리스트**

### **완료:**
- [x] `interfaces.py` - 인터페이스 정의
- [x] `simulation.py` - 시뮬레이션 구현
- [x] `alpaca_api.py` - 실제 Alpaca 구현
- [x] `plaid_api.py` - 실제 Plaid 구현
- [x] `factory.py` - 팩토리 패턴
- [x] `trading_service.py` - 투자 서비스
- [x] `plaid_service.py` - Plaid 연동 서비스

### **다음 단계:**
- [ ] 시뮬레이션 모드 테스트
- [ ] 실제 API 연동 테스트
- [ ] 환경변수 전환 테스트

---

## ⚠️ **주의사항**

### **1. 시뮬레이션 모드 제한사항**
- 포지션/주문이 메모리에만 저장 (서버 재시작 시 초기화)
- 실제로는 DB에 저장하는 모델 추가 필요

### **2. 실제 API 전환 시**
- Paper Trading으로 먼저 테스트
- 충분한 테스트 후 Live Trading 전환
- 에러 처리 강화

### **3. 데이터 일관성**
- 시뮬레이션과 실제 API 간 데이터 동기화 필요
- 포지션 동기화 로직 구현

---

**작성자**: AI Assistant  
**업데이트**: 2024.11.07

