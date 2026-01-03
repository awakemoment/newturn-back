# 🚀 Newturn 배포 가이드 (빠른 시작)

**대상**: Railway + Supabase + Upstash + Vercel  
**비용**: $5/월  
**예상 시간**: 1-2시간

---

## 📋 **사전 준비사항**

- [ ] GitHub 계정 (코드 저장소)
- [ ] Railway 계정 (https://railway.app)
- [ ] Supabase 계정 (https://supabase.com)
- [ ] Upstash 계정 (https://upstash.com)
- [ ] Vercel 계정 (https://vercel.com)

---

## 🗄️ **1단계: Supabase 데이터베이스 설정 (10분)**

1. https://supabase.com 접속 → "Start your project" → GitHub 로그인
2. "New Project" 클릭
3. 설정:
   - **Name**: `newturn-production`
   - **Database Password**: 강력한 비밀번호 생성 (저장!)
   - **Region**: `Southeast Asia (Singapore)` 또는 가장 가까운 지역
   - **Pricing Plan**: Free
4. 프로젝트 생성 완료 대기 (2-3분)
5. **Settings** → **Database** → **Connection string** → **URI** 복사
   - 예: `postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres`

✅ **완료**: DATABASE_URL 저장

---

## 🔴 **2단계: Upstash Redis 설정 (5분)**

1. https://upstash.com 접속 → "Start for Free" → GitHub 로그인
2. "Create Database" 클릭
3. 설정:
   - **Name**: `newturn-redis`
   - **Type**: Regional (무료)
   - **Region**: `ap-northeast-1` (Tokyo) 또는 `ap-southeast-1` (Singapore)
   - **TLS**: Enabled
4. "Create" 클릭
5. Redis 데이터베이스 클릭 → **Redis URL** 복사
   - 예: `redis://default:[TOKEN]@xxxxx.upstash.io:6379`

✅ **완료**: REDIS_URL 저장

---

## 🚂 **3단계: Railway 백엔드 배포 (30분)**

### **3.1 프로젝트 생성**

1. https://railway.app 접속 → GitHub 로그인
2. "New Project" → "Deploy from GitHub repo"
3. Newturn 백엔드 저장소 선택

### **3.2 환경변수 설정**

Railway 대시보드 → 서비스 → **Variables** 탭에서 추가:

#### **기본 설정**
```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=[랜덤 문자열 50자 이상]
DEBUG=False
```

**SECRET_KEY 생성:**
```python
# Python에서 실행
import secrets
print(secrets.token_urlsafe(50))
```

#### **데이터베이스**
```env
DATABASE_URL=[Supabase URI 복사한 값]
```

#### **Redis**
```env
REDIS_URL=[Upstash Redis URL]
CELERY_BROKER_URL=[Upstash Redis URL]
CELERY_RESULT_BACKEND=[Upstash Redis URL]
```

#### **CORS**
```env
CORS_ORIGIN=https://newturn.vercel.app
```

#### **도메인**
```env
ALLOWED_HOSTS=api.newturn.com,*.railway.app
```

#### **API 키들**
```env
PLAID_CLIENT_ID=[Plaid Client ID]
PLAID_SECRET=[Plaid Secret]
PLAID_ENV=sandbox
ALPACA_API_KEY=[Alpaca API Key]
ALPACA_SECRET_KEY=[Alpaca Secret Key]
ALPACA_BASE_URL=https://paper-api.alpaca.markets
POLYGON_API_KEY=[Polygon.io API Key]  # 선택사항
```

### **3.3 배포**

1. Railway 대시보드에서 **"Deploy"** 버튼 클릭
2. 또는 GitHub에 커밋/푸시하면 자동 배포
3. 배포 로그 확인 (오류 발생 시 확인)

### **3.4 데이터베이스 마이그레이션**

**방법 1: Railway CLI (권장)**
```bash
# Railway CLI 설치
npm i -g @railway/cli

# 로그인
railway login

# 프로젝트 연결
railway link

# 마이그레이션 실행
railway run python manage.py migrate

# 슈퍼유저 생성 (선택사항)
railway run python manage.py createsuperuser

# 정적 파일 수집
railway run python manage.py collectstatic --noinput
```

**방법 2: Railway 대시보드**
1. Railway 대시보드 → 서비스 → **"View Logs"**
2. **"Open Terminal"** 클릭
3. 다음 명령어 실행:
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser  # 선택사항
```

### **3.5 도메인 설정**

1. Railway 대시보드 → 서비스 → **Settings** → **Domains**
2. **"Generate Domain"** 클릭
3. 생성된 도메인 확인: `newturn-production.up.railway.app`
4. 커스텀 도메인 설정 (선택사항): `api.newturn.com`

✅ **완료**: 백엔드 배포 완료

---

## 🎨 **4단계: Vercel 프론트엔드 배포 (20분)**

### **4.1 프로젝트 생성**

1. https://vercel.com 접속 → GitHub 로그인
2. **"Add New..."** → **"Project"** 클릭
3. Newturn 프론트엔드 저장소 선택
4. **Root Directory**: `apps/investor` (또는 프론트엔드 루트)
5. **Framework Preset**: Next.js (자동 감지)

### **4.2 환경변수 설정**

Vercel 대시보드 → 프로젝트 → **Settings** → **Environment Variables**:

```env
NEXT_PUBLIC_API_URL=https://api.newturn.com
# 또는 Railway 도메인: https://newturn-production.up.railway.app
```

### **4.3 배포**

1. **"Deploy"** 버튼 클릭
2. 배포 완료 대기 (2-3분)
3. 생성된 도메인 확인: `newturn.vercel.app`

### **4.4 커스텀 도메인 설정 (선택사항)**

1. Vercel 대시보드 → 프로젝트 → **Settings** → **Domains**
2. 도메인 추가: `newturn.com`
3. DNS 설정 안내 따르기

✅ **완료**: 프론트엔드 배포 완료

---

## ✅ **5단계: 배포 확인 (5분)**

### **백엔드 API 테스트**

```bash
# Health check
curl https://newturn-production.up.railway.app/api/health/

# 또는 커스텀 도메인
curl https://api.newturn.com/api/health/
```

### **프론트엔드 테스트**

1. 브라우저에서 프론트엔드 URL 접속
2. 로그인 테스트
3. 주요 기능 테스트

---

## 🚨 **문제 해결**

### **배포 실패**
- Railway/Vercel 배포 로그 확인
- 환경변수 모두 설정되었는지 확인
- `requirements/production.txt` 확인

### **데이터베이스 연결 실패**
- Supabase URI 형식 확인
- Supabase 프로젝트 비밀번호 확인
- Supabase 대시보드 → Settings → Database → Connection Pooling 확인

### **Redis 연결 실패**
- Upstash Redis URL 형식 확인
- Upstash 토큰 확인

### **CORS 오류**
- CORS_ORIGIN이 프론트엔드 URL과 일치하는지 확인
- `http://` vs `https://` 확인

---

## 📊 **최종 구성 확인**

```
✅ Frontend: Vercel (무료)
   URL: https://newturn.vercel.app

✅ Backend: Railway ($5/월)
   URL: https://newturn-production.up.railway.app

✅ Database: Supabase (무료, 500MB)
   URI: postgresql://postgres:...@db.xxxxx.supabase.co:5432/postgres

✅ Redis: Upstash (무료)
   URL: redis://default:...@xxxxx.upstash.io:6379

✅ 총 비용: $5/월
```

---

## 📚 **참고 자료**

- [Railway Django 가이드](https://docs.railway.app/guides/django)
- [Supabase Django 가이드](https://supabase.com/docs/guides/getting-started/quickstarts/django)
- [Upstash Redis 가이드](https://docs.upstash.com/redis)
- [Vercel Next.js 가이드](https://vercel.com/docs/frameworks/nextjs)

---

**마지막 업데이트**: 2025.01.14

