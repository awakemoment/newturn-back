# 🧪 API 테스트 가이드

**작성일**: 2024.11.07  
**목적**: 계좌 API 엔드포인트 테스트 방법

---

## 🚀 **테스트 준비**

### **1. 백엔드 서버 실행**

```bash
cd business/newturn-back
conda activate newturn_back
python manage.py runserver
```

### **2. 프론트엔드 서버 실행**

```bash
cd business/newturn-front/apps/investor
npm run dev
```

---

## 📋 **API 엔드포인트 목록**

### **카테고리 통장**

#### **1. 통장 목록 조회**
```http
GET /api/accounts/category-accounts/
Authorization: Token {token}
```

**응답:**
```json
[
  {
    "id": 1,
    "name": "카페/베이커리 통장",
    "category": "coffee",
    "balance": "70.00",
    "monthly_budget": "100.00",
    "current_month_spent": "30.00",
    ...
  }
]
```

#### **2. 통장 생성**
```http
POST /api/accounts/category-accounts/
Authorization: Token {token}
Content-Type: application/json

{
  "name": "카페/베이커리 통장",
  "category": "coffee",
  "monthly_budget": "100.00"
}
```

#### **3. 입금**
```http
POST /api/accounts/category-accounts/{id}/deposit/
Authorization: Token {token}
Content-Type: application/json

{
  "amount": "100.00",
  "note": "월급 입금"
}
```

#### **4. 출금**
```http
POST /api/accounts/category-accounts/{id}/withdraw/
Authorization: Token {token}
Content-Type: application/json

{
  "amount": "5.00",
  "merchant_name": "스타벅스",
  "category_detail": "아메리카노",
  "note": "커피 구매"
}
```

#### **5. 절약 금액 계산**
```http
GET /api/accounts/category-accounts/{id}/monthly-savings/
Authorization: Token {token}
```

**응답:**
```json
{
  "savings": "70.00"
}
```

#### **6. 절약 금액으로 투자**
```http
POST /api/accounts/category-accounts/{id}/invest-savings/
Authorization: Token {token}
Content-Type: application/json

{
  "stock_id": 123
}
```

**응답:**
```json
{
  "id": 1,
  "account": 1,
  "savings_amount": "70.00",
  "stock": {
    "id": 123,
    "stock_code": "NVDA",
    "stock_name": "NVIDIA CORP"
  },
  "purchase_price": "500.00",
  "shares": "0.1400",
  "status": "invested",
  ...
}
```

#### **7. 거래 내역 조회**
```http
GET /api/accounts/category-accounts/{id}/transactions/
Authorization: Token {token}
```

---

### **절약 리워드 (투자)**

#### **1. 투자 목록 조회**
```http
GET /api/accounts/savings-rewards/
Authorization: Token {token}
```

#### **2. 투자 상세 조회**
```http
GET /api/accounts/savings-rewards/{id}/
Authorization: Token {token}
```

#### **3. 매도**
```http
POST /api/accounts/savings-rewards/{id}/sell/
Authorization: Token {token}
```

**응답:**
```json
{
  "success": true,
  "net_proceeds": "75.00",
  "return_rate": "7.14",
  "reward": { ... }
}
```

---

### **예치금 계좌**

#### **1. 예치금 계좌 조회**
```http
GET /api/accounts/deposit-account/
Authorization: Token {token}
```

---

## 🧪 **테스트 시나리오**

### **시나리오 1: 통장 생성 → 입금 → 출금 → 절약 계산**

```bash
# 1. 통장 생성
curl -X POST http://localhost:8000/api/accounts/category-accounts/ \
  -H "Authorization: Token {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "카페/베이커리 통장",
    "category": "coffee",
    "monthly_budget": "100.00"
  }'

# 2. 입금
curl -X POST http://localhost:8000/api/accounts/category-accounts/1/deposit/ \
  -H "Authorization: Token {token}" \
  -H "Content-Type: application/json" \
  -d '{"amount": "100.00", "note": "월급 입금"}'

# 3. 출금
curl -X POST http://localhost:8000/api/accounts/category-accounts/1/withdraw/ \
  -H "Authorization: Token {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "30.00",
    "merchant_name": "스타벅스",
    "category_detail": "아메리카노"
  }'

# 4. 절약 계산
curl -X GET http://localhost:8000/api/accounts/category-accounts/1/monthly-savings/ \
  -H "Authorization: Token {token}"
```

### **시나리오 2: 절약 금액으로 투자**

```bash
# 1. 절약 금액 확인
curl -X GET http://localhost:8000/api/accounts/category-accounts/1/monthly-savings/ \
  -H "Authorization: Token {token}"

# 2. 투자 실행
curl -X POST http://localhost:8000/api/accounts/category-accounts/1/invest-savings/ \
  -H "Authorization: Token {token}" \
  -H "Content-Type: application/json" \
  -d '{"stock_id": 123}'

# 3. 투자 목록 확인
curl -X GET http://localhost:8000/api/accounts/savings-rewards/ \
  -H "Authorization: Token {token}"
```

### **시나리오 3: 매도 (수익일 때)**

```bash
# 1. 투자 상세 확인
curl -X GET http://localhost:8000/api/accounts/savings-rewards/1/ \
  -H "Authorization: Token {token}"

# 2. 매도 (can_sell이 true일 때만)
curl -X POST http://localhost:8000/api/accounts/savings-rewards/1/sell/ \
  -H "Authorization: Token {token}"
```

---

## 🔍 **테스트 체크리스트**

### **기본 기능**
- [ ] 통장 생성
- [ ] 통장 목록 조회
- [ ] 통장 상세 조회
- [ ] 입금
- [ ] 출금
- [ ] 절약 금액 계산

### **투자 기능**
- [ ] 절약 금액으로 투자
- [ ] 투자 목록 조회
- [ ] 투자 상세 조회
- [ ] 주가 업데이트 (시뮬레이션)
- [ ] 매도 (수익일 때)
- [ ] 매도 불가 (손실일 때)

### **에러 처리**
- [ ] 인증 없이 접근 시 401
- [ ] 존재하지 않는 리소스 접근 시 404
- [ ] 잘못된 데이터 입력 시 400
- [ ] 잔액 부족 시 에러

---

## 🐛 **문제 해결**

### **1. 인증 에러 (401)**
- 로그인 후 토큰 발급 필요
- `Authorization: Token {token}` 헤더 확인

### **2. 주가 데이터 없음**
- StockPrice 테이블에 데이터가 있어야 함
- 시뮬레이션 모드는 StockPrice 테이블 사용

### **3. 예치금 부족**
- DepositAccount에 충분한 잔액 필요
- 시뮬레이션 모드에서는 자동으로 처리

---

**작성자**: AI Assistant  
**업데이트**: 2024.11.07

