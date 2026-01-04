# 🚂 Railway 환경변수 설정 가이드

**작성일**: 2025.01.14  
**목적**: Railway 배포를 위한 환경변수 목록

---

## 📋 **필수 환경변수 목록**

Railway 대시보드 → 서비스 → **Variables** 탭에서 다음 환경변수들을 추가하세요.

---

## 🔧 **기본 Django 설정**

### **1. DJANGO_SETTINGS_MODULE**
```
Key: DJANGO_SETTINGS_MODULE
Value: config.settings.production
```

### **2. SECRET_KEY**
```
Key: SECRET_KEY
Value: [랜덤 문자열 50자 이상 생성]
```

**생성 방법:**
```python
# Python에서 실행
import secrets
print(secrets.token_urlsafe(50))
```

또는 터미널:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### **3. DEBUG**
```
Key: DEBUG
Value: False
```

---

## 🗄️ **데이터베이스 (Supabase)**

### **4. DATABASE_URL**
```
Key: DATABASE_URL
Value: postgresql://postgres:@AB4832299cd@db.uczmhthbebuptmkrvbdh.supabase.co:5432/postgres
```

**⚠️ 주의**: 비밀번호는 실제 값으로 교체하세요.

---

## 🔴 **Redis (Upstash)**

### **5. REDIS_URL**
```
Key: REDIS_URL
Value: rediss://default:AUWOAAIncDIzNDE3ODVmMDY3ZmM0YTRkODVmZjcwMGJlZWRlZjdiZnAyMTc4MDY@stable-mackerel-17806.upstash.io:6379
```

### **6. CELERY_BROKER_URL**
```
Key: CELERY_BROKER_URL
Value: rediss://default:AUWOAAIncDIzNDE3ODVmMDY3ZmM0YTRkODVmZjcwMGJlZWRlZjdiZnAyMTc4MDY@stable-mackerel-17806.upstash.io:6379
```
*(REDIS_URL과 동일한 값)*

### **7. CELERY_RESULT_BACKEND**
```
Key: CELERY_RESULT_BACKEND
Value: rediss://default:AUWOAAIncDIzNDE3ODVmMDY3ZmM0YTRkODVmZjcwMGJlZWRlZjdiZnAyMTc4MDY@stable-mackerel-17806.upstash.io:6379
```
*(REDIS_URL과 동일한 값)*

---

## 🌐 **CORS 및 도메인 설정**

### **8. CORS_ORIGIN**
```
Key: CORS_ORIGIN
Value: https://newturn.vercel.app
```
*(또는 프론트엔드 도메인)*

### **9. ALLOWED_HOSTS**
```
Key: ALLOWED_HOSTS
Value: api.newturn.com,*.railway.app
```
*(Railway 자동 도메인 포함)*

---

## 💳 **Plaid (은행 계좌 연동)**

### **10. PLAID_CLIENT_ID**
```
Key: PLAID_CLIENT_ID
Value: [Plaid Client ID]
```
*(Plaid 대시보드에서 확인)*

### **11. PLAID_SECRET**
```
Key: PLAID_SECRET
Value: [Plaid Secret Key]
```
*(Plaid 대시보드에서 확인)*

### **12. PLAID_ENV**
```
Key: PLAID_ENV
Value: sandbox
```
*(또는 production)*

---

## 📈 **Alpaca (주식 거래)**

### **13. ALPACA_API_KEY**
```
Key: ALPACA_API_KEY
Value: [Alpaca API Key]
```
*(Alpaca 대시보드에서 확인)*

### **14. ALPACA_SECRET_KEY**
```
Key: ALPACA_SECRET_KEY
Value: [Alpaca Secret Key]
```
*(Alpaca 대시보드에서 확인)*

### **15. ALPACA_BASE_URL**
```
Key: ALPACA_BASE_URL
Value: https://paper-api.alpaca.markets
```
*(Paper trading용, 실제 거래 시: https://api.alpaca.markets)*

---

## 📊 **기타 API 키 (선택사항)**

### **16. POLYGON_API_KEY**
```
Key: POLYGON_API_KEY
Value: [Polygon.io API Key]
```
*(선택사항, 주가 데이터 수집용)*

### **17. OPENAI_API_KEY**
```
Key: OPENAI_API_KEY
Value: [OpenAI API Key]
```
*(선택사항, 10-K 분석용)*

### **18. STRIPE_SECRET_KEY**
```
Key: STRIPE_SECRET_KEY
Value: [Stripe Secret Key]
```
*(선택사항, 결제 시스템용)*

---

## 🔔 **에러 트래킹 (선택사항)**

### **19. SENTRY_DSN**
```
Key: SENTRY_DSN
Value: [Sentry DSN]
```
*(선택사항, Sentry 사용 시)*

---

## 📧 **이메일 설정 (선택사항)**

### **20. EMAIL_HOST**
```
Key: EMAIL_HOST
Value: smtp.gmail.com
```
*(또는 SendGrid, AWS SES)*

### **21. EMAIL_HOST_USER**
```
Key: EMAIL_HOST_USER
Value: [이메일 주소]
```

### **22. EMAIL_HOST_PASSWORD**
```
Key: EMAIL_HOST_PASSWORD
Value: [이메일 비밀번호 또는 앱 비밀번호]
```

### **23. DEFAULT_FROM_EMAIL**
```
Key: DEFAULT_FROM_EMAIL
Value: noreply@newturn.com
```

---

## ✅ **최소 필수 환경변수 (즉시 배포용)**

배포를 바로 시작하려면 다음 환경변수만 필수입니다:

```
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=[생성된 랜덤 문자열]
DEBUG=False
DATABASE_URL=postgresql://postgres:@AB4832299cd@db.uczmhthbebuptmkrvbdh.supabase.co:5432/postgres
REDIS_URL=rediss://default:AUWOAAIncDIzNDE3ODVmMDY3ZmM0YTRkODVmZjcwMGJlZWRlZjdiZnAyMTc4MDY@stable-mackerel-17806.upstash.io:6379
CELERY_BROKER_URL=[REDIS_URL과 동일]
CELERY_RESULT_BACKEND=[REDIS_URL과 동일]
CORS_ORIGIN=https://newturn.vercel.app
ALLOWED_HOSTS=api.newturn.com,*.railway.app
```

나머지는 기능별로 필요할 때 추가하세요.

---

## 📝 **Railway에서 설정하는 방법**

1. Railway 대시보드 → 프로젝트 → 서비스 선택
2. **"Variables"** 탭 클릭
3. **"New Variable"** 버튼 클릭
4. Key와 Value 입력
5. **"Add"** 클릭
6. 모든 환경변수 추가 완료 후 저장

---

## 🔐 **보안 주의사항**

- ✅ **절대 공개하지 마세요**: SECRET_KEY, API 키, 비밀번호
- ✅ **Git에 커밋하지 마세요**: `.env` 파일은 `.gitignore`에 포함
- ✅ **Railway Variables만 사용**: 환경변수는 Railway 대시보드에서만 관리
- ✅ **정기적으로 비밀번호 변경**: 특히 SECRET_KEY

---

**마지막 업데이트**: 2025.01.14

