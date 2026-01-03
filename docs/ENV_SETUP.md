# ⚙️ 환경변수 설정 가이드

**작성일**: 2024.11.07  
**목적**: 시뮬레이션/실제 API 모드 전환을 위한 환경변수 설정

---

## 🔧 **환경변수 목록**

### **시뮬레이션 모드 (기본)**

```bash
# .env 파일

# 브로커 API 모드
USE_SIMULATION_BROKER=True

# 은행 API 모드
USE_SIMULATION_BANK=True
```

### **실제 API 모드**

```bash
# .env 파일

# 브로커 API 모드
USE_SIMULATION_BROKER=False

# Alpaca API 설정
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_PAPER=True  # Paper Trading (True) 또는 Live Trading (False)

# 은행 API 모드
USE_SIMULATION_BANK=False

# Plaid API 설정
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_secret_here
PLAID_ENV=sandbox  # sandbox, development, production
```

---

## 🔄 **모드 전환 방법**

### **시뮬레이션 → 실제 API**

1. `.env` 파일 수정
   ```bash
   USE_SIMULATION_BROKER=False
   USE_SIMULATION_BANK=False
   ```

2. API 키 설정
   ```bash
   ALPACA_API_KEY=...
   ALPACA_SECRET_KEY=...
   PLAID_CLIENT_ID=...
   PLAID_SECRET=...
   ```

3. 서버 재시작
   ```bash
   python manage.py runserver
   ```

4. 코드 변경 없음! ✅

### **실제 API → 시뮬레이션**

1. `.env` 파일 수정
   ```bash
   USE_SIMULATION_BROKER=True
   USE_SIMULATION_BANK=True
   ```

2. 서버 재시작

---

## 🧪 **테스트 환경 설정**

### **개발 환경 (시뮬레이션)**

```bash
# .env.development
USE_SIMULATION_BROKER=True
USE_SIMULATION_BANK=True
```

### **스테이징 환경 (Paper Trading)**

```bash
# .env.staging
USE_SIMULATION_BROKER=False
USE_SIMULATION_BANK=False
ALPACA_API_KEY=staging_key
ALPACA_SECRET_KEY=staging_secret
ALPACA_PAPER=True  # Paper Trading
PLAID_CLIENT_ID=staging_client_id
PLAID_SECRET=staging_secret
PLAID_ENV=sandbox
```

### **프로덕션 환경 (Live Trading)**

```bash
# .env.production
USE_SIMULATION_BROKER=False
USE_SIMULATION_BANK=False
ALPACA_API_KEY=production_key
ALPACA_SECRET_KEY=production_secret
ALPACA_PAPER=False  # Live Trading
PLAID_CLIENT_ID=production_client_id
PLAID_SECRET=production_secret
PLAID_ENV=production
```

---

## 📝 **환경변수 로드**

### **Django settings.py**

```python
# config/settings/local.py

import os
from dotenv import load_dotenv

load_dotenv()

# 브로커 API 모드
USE_SIMULATION_BROKER = os.getenv('USE_SIMULATION_BROKER', 'True').lower() == 'true'

# Alpaca API
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', '')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', '')
ALPACA_PAPER = os.getenv('ALPACA_PAPER', 'True').lower() == 'true'

# 은행 API 모드
USE_SIMULATION_BANK = os.getenv('USE_SIMULATION_BANK', 'True').lower() == 'true'

# Plaid API
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID', '')
PLAID_SECRET = os.getenv('PLAID_SECRET', '')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
```

---

## ⚠️ **주의사항**

1. **API 키 보안**
   - `.env` 파일은 Git에 커밋하지 않기
   - `.gitignore`에 `.env` 추가
   - 프로덕션에서는 환경변수로 직접 설정

2. **모드 확인**
   - 서버 시작 시 로그에 현재 모드 표시
   - 개발 중 실수로 Live Trading 사용 방지

3. **테스트 순서**
   - 시뮬레이션 → Paper Trading → Live Trading
   - 각 단계에서 충분한 테스트

---

**작성자**: AI Assistant  
**업데이트**: 2024.11.07

