# 🚀 Newturn 배포 가이드 (권장 구성)

**대상**: Railway + Supabase + Upstash + Vercel  
**비용**: $5/월  
**예상 시간**: 1-2시간

---

## 📋 **사전 준비사항**

### **필수 계정**
- [ ] GitHub 계정 (코드 저장소)
- [ ] Railway 계정 (https://railway.app)
- [ ] Supabase 계정 (https://supabase.com)
- [ ] Upstash 계정 (https://upstash.com)
- [ ] Vercel 계정 (https://vercel.com)

### **필수 정보**
- [ ] 도메인 (선택사항, 무료 도메인도 가능)
- [ ] 환경변수 목록 확인

---

## 🗄️ **1단계: Supabase 데이터베이스 설정**

### **1.1 Supabase 프로젝트 생성**

1. https://supabase.com 접속
2. "Start your project" 클릭
3. GitHub 계정으로 로그인
4. "New Project" 클릭
5. 프로젝트 설정:
   - **Name**: `newturn-production`
   - **Database Password**: 강력한 비밀번호 생성 (저장해두세요!)
   - **Region**: `Southeast Asia (Singapore)` 또는 가장 가까운 지역
   - **Pricing Plan**: Free

6. "Create new project" 클릭
7. 프로젝트 생성 완료까지 2-3분 대기

### **1.2 데이터베이스 연결 정보 확인**

1. 프로젝트 대시보드에서 왼쪽 사이드바 → **Settings** → **Database** 클릭
2. **Connection string** 섹션에서 **URI** 복사
   - 예: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`

3. **Connection pooling** 섹션에서 **Session mode** URI도 복사 (선택사항, 성능 향상)
   - 예: `postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres`

**중요**: 이 URI를 환경변수로 사용합니다.

### **1.3 데이터베이스 설정 완료**

✅ Supabase PostgreSQL 준비 완료  
✅ 연결 URI 저장 완료

---

## 🔴 **2단계: Upstash Redis 설정**

### **2.1 Upstash 프로젝트 생성**

1. https://upstash.com 접속
2. "Start for Free" 클릭
3. GitHub 계정으로 로그인
4. 대시보드에서 **"Create Database"** 클릭
5. Redis 설정:
   - **Name**: `newturn-redis`
   - **Type**: Regional (무료)
   - **Region**: `ap-northeast-1` (Tokyo, 한국에서 가장 가까움) 또는 `ap-southeast-1` (Singapore)
   - **TLS**: Enabled (기본값)

6. "Create" 클릭

### **2.2 Redis 연결 정보 확인**

1. 생성된 Redis 데이터베이스 클릭
2. **REST API** 또는 **Redis CLI** 탭에서 연결 정보 확인:
   - **UPSTASH_REDIS_REST_URL**: `https://xxxxx.upstash.io`
   - **UPSTASH_REDIS_REST_TOKEN**: `xxxxxxxxxxxxx`

3. 또는 **Redis URL** 형식:
   - `redis://default:xxxxx@xxxxx.upstash.io:6379`

**Django/Celery용 Redis URL 형식:**
```
redis://default:[TOKEN]@[ENDPOINT]:6379
```

**중요**: Upstash는 REST API 기반이므로 Django의 Redis 백엔드와 호환되지만, Celery는 `redis://` URL 형식을 사용해야 합니다.

### **2.3 Upstash Redis 설정 완료**

✅ Upstash Redis 준비 완료  
✅ Redis URL 저장 완료

---

## 🚂 **3단계: Railway 백엔드 배포**

### **3.1 Railway 프로젝트 생성**

1. https://railway.app 접속
2. GitHub 계정으로 로그인
3. "New Project" 클릭
4. "Deploy from GitHub repo" 선택
5. GitHub 저장소 선택:
   - Newturn 백엔드 저장소 선택
   - 브랜치: `main` 또는 `master`

### **3.2 Django 서비스 생성**

1. Railway 대시보드에서 **"New"** → **"Empty Service"** 클릭
2. 서비스 이름: `newturn-backend`
3. GitHub 저장소 연결 (이미 연결됨)

### **3.3 환경변수 설정**

Railway 대시보드에서 **Variables** 탭 클릭 후 다음 환경변수 추가:

#### **기본 Django 설정**
```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=[강력한 랜덤 문자열 생성, 50자 이상]
DEBUG=False
```

**SECRET_KEY 생성 방법:**
```python
# Python에서 실행
import secrets
print(secrets.token_urlsafe(50))
```

#### **데이터베이스 (Supabase)**
```env
DATABASE_URL=[Supabase URI 복사한 값]
# 예: postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

#### **Redis (Upstash)**
```env
REDIS_URL=[Upstash Redis URL]
# 예: redis://default:[TOKEN]@xxxxx.upstash.io:6379
CELERY_BROKER_URL=[Upstash Redis URL]
CELERY_RESULT_BACKEND=[Upstash Redis URL]
```

#### **CORS 설정**
```env
CORS_ORIGIN=https://newturn.vercel.app
# 또는 커스텀 도메인: https://newturn.com
```

#### **도메인 설정**
```env
ALLOWED_HOSTS=api.newturn.com,*.railway.app
# Railway 자동 도메인: newturn-production.up.railway.app
```

#### **Plaid 설정 (투자 시스템)**
```env
PLAID_CLIENT_ID=[Plaid Client ID]
PLAID_SECRET=[Plaid Secret]
PLAID_ENV=sandbox  # 또는 production
```

#### **Alpaca 설정 (주식 거래)**
```env
ALPACA_API_KEY=[Alpaca API Key]
ALPACA_SECRET_KEY=[Alpaca Secret Key]
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # Paper trading
# 또는 https://api.alpaca.markets (Live trading)
```

#### **기타 API 키**
```env
POLYGON_API_KEY=[Polygon.io API Key]  # 선택사항
```

### **3.4 Railway 설정 파일 생성**

프로젝트 루트에 `railway.json` 또는 `railway.toml` 파일 생성 (선택사항):

**railway.toml**:
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "gunicorn config.wsgi.base:application --bind 0.0.0.0:$PORT"
healthcheckPath = "/"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### **3.5 Nixpacks 설정 (자동 감지)**

Railway는 자동으로 Python 프로젝트를 감지합니다. 다음 파일들이 있으면 자동 설정:

- `requirements.txt` 또는 `requirements/production.txt`
- `manage.py`
- `Procfile` (선택사항)

**Procfile** 생성 (프로젝트 루트):
```
web: gunicorn config.wsgi.base:application --bind 0.0.0.0:$PORT
worker: celery -A newturn worker -l info
beat: celery -A newturn beat -l info
```

**중요**: Railway의 무료 티어에서는 Worker와 Beat을 별도 서비스로 실행할 수 없습니다. 하나의 서비스에서만 실행됩니다. Celery Worker/Beat은 나중에 추가하거나 Cron Job으로 대체할 수 있습니다.

### **3.6 requirements/production.txt 확인**

`requirements/production.txt`에 다음이 포함되어 있는지 확인:

```txt
# Database
psycopg2-binary>=2.9.0

# Server
gunicorn>=21.0.0

# Static files (WhiteNoise)
whitenoise>=6.0.0

# Redis
redis>=5.0.0
hiredis>=2.2.0  # 선택사항, 성능 향상

# Celery
celery>=5.3.0
```

### **3.7 production.py 수정**

`config/settings/production.py`를 Railway/Supabase/Upstash에 맞게 수정:

```python
from .base import *
import dj_database_url

# ==================
# Railway + Supabase + Upstash 배포 환경 설정
# ==================

DEBUG = False

ALLOWED_HOSTS = [
    'api.newturn.com',
    '.railway.app',
    '.up.railway.app',
]

# CORS 설정
CORS_ALLOWED_ORIGINS = [
    'https://newturn.vercel.app',
    'https://newturn.com',
    'https://www.newturn.com',
]
CORS_ALLOW_CREDENTIALS = True

# Database - Supabase PostgreSQL
DATABASES = {
    'default': dj_database_url.config(
        default=env('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Static/Media Files - WhiteNoise
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Redis - Upstash
REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    }
}

# Celery
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default=REDIS_URL)
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default=REDIS_URL)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# 보안 설정
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Sentry (선택사항)
SENTRY_DSN = env('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )

# 로깅
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### **3.8 배포**

1. Railway 대시보드에서 **"Deploy"** 버튼 클릭
2. 또는 GitHub에 커밋/푸시하면 자동 배포
3. 배포 로그 확인:
   - **Deployments** 탭에서 실시간 로그 확인
   - 오류 발생 시 로그 확인

### **3.9 데이터베이스 마이그레이션**

배포가 완료되면 Railway 콘솔에서 마이그레이션 실행:

**방법 1: Railway CLI 사용**
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

**방법 2: Railway 대시보드에서 실행**
1. Railway 대시보드 → 서비스 → **"View Logs"**
2. **"Open Terminal"** 클릭
3. 다음 명령어 실행:
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser  # 선택사항
```

### **3.10 도메인 설정**

1. Railway 대시보드 → 서비스 → **Settings** → **Domains**
2. **"Generate Domain"** 클릭
3. 생성된 도메인 확인: `newturn-production.up.railway.app`
4. 커스텀 도메인 설정 (선택사항):
   - **"Custom Domain"** 입력: `api.newturn.com`
   - DNS 설정 필요 (Railway가 안내)

### **3.11 Railway 배포 완료**

✅ Django 서버 배포 완료  
✅ 환경변수 설정 완료  
✅ 데이터베이스 마이그레이션 완료  
✅ 도메인 설정 완료

---

## 🎨 **4단계: Vercel 프론트엔드 배포**

### **4.1 Vercel 프로젝트 생성**

1. https://vercel.com 접속
2. GitHub 계정으로 로그인
3. **"Add New..."** → **"Project"** 클릭
4. GitHub 저장소 선택:
   - Newturn 프론트엔드 저장소 선택
   - **Root Directory**: `apps/investor` (또는 프론트엔드 루트)
   - **Framework Preset**: Next.js (자동 감지)

### **4.2 빌드 설정**

**Build Command**: (기본값 사용)
```
pnpm build
```

**Output Directory**: (기본값 사용)
```
.next
```

**Install Command**: (기본값 사용)
```
pnpm install
```

### **4.3 환경변수 설정**

Vercel 대시보드 → 프로젝트 → **Settings** → **Environment Variables**:

```env
NEXT_PUBLIC_API_URL=https://api.newturn.com
# 또는 Railway 도메인: https://newturn-production.up.railway.app
```

### **4.4 배포**

1. **"Deploy"** 버튼 클릭
2. 배포 완료까지 2-3분 대기
3. 생성된 도메인 확인: `newturn.vercel.app`

### **4.5 커스텀 도메인 설정 (선택사항)**

1. Vercel 대시보드 → 프로젝트 → **Settings** → **Domains**
2. 도메인 추가: `newturn.com`
3. DNS 설정 안내 따르기:
   - A 레코드 또는 CNAME 레코드 설정
   - DNS 전파 대기 (최대 24시간, 보통 몇 분)

### **4.6 Vercel 배포 완료**

✅ Next.js 앱 배포 완료  
✅ 환경변수 설정 완료  
✅ 도메인 설정 완료

---

## ✅ **5단계: 배포 확인 및 테스트**

### **5.1 백엔드 API 테스트**

```bash
# Health check
curl https://api.newturn.com/api/health/
# 또는
curl https://newturn-production.up.railway.app/api/health/

# 인증 테스트
curl https://api.newturn.com/api/auth/me/
```

### **5.2 프론트엔드 테스트**

1. 브라우저에서 프론트엔드 URL 접속
2. 로그인 테스트
3. 주요 기능 테스트

### **5.3 데이터베이스 연결 확인**

Railway 콘솔에서:
```bash
railway run python manage.py dbshell
# 또는
python manage.py dbshell
```

Supabase 대시보드에서:
- **Table Editor**에서 테이블 확인
- 데이터 확인

### **5.4 Redis 연결 확인**

Railway 콘솔에서:
```python
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'hello')
>>> cache.get('test')
'hello'
```

---

## 🔧 **6단계: 추가 설정 (선택사항)**

### **6.1 Celery Worker/Beat 설정**

Railway 무료 티어에서는 Worker와 Beat을 별도 서비스로 실행할 수 없습니다.

**옵션 1: Cron Job 사용 (권장)**
- Railway의 Cron Job 기능 사용
- 또는 외부 Cron 서비스 (cron-job.org, EasyCron)

**옵션 2: 업그레이드 플랜**
- Railway Pro 플랜 ($20/월)으로 업그레이드
- Worker와 Beat을 별도 서비스로 실행

**옵션 3: 단일 프로세스**
- Gunicorn + Celery Worker를 같은 프로세스에서 실행 (권장하지 않음)

### **6.2 Sentry 에러 트래킹 (선택사항)**

1. https://sentry.io 가입
2. Django 프로젝트 생성
3. DSN 복사
4. Railway 환경변수 추가:
```env
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

### **6.3 백업 설정**

**Supabase 백업:**
- Supabase는 자동으로 백업합니다 (Free 플랜: 7일 보관)
- Pro 플랜: Point-in-Time Recovery (PITR)

**수동 백업:**
```bash
# Railway 콘솔에서
railway run python manage.py dumpdata > backup.json
```

---

## 📊 **비용 요약**

| 서비스 | 플랜 | 월 비용 |
|--------|------|---------|
| Vercel | Free | $0 |
| Railway | Starter | $5 |
| Supabase | Free | $0 |
| Upstash | Free | $0 |
| **총계** | | **$5/월** |

---

## 🚨 **문제 해결**

### **배포 실패**

1. **로그 확인**: Railway/Vercel 배포 로그 확인
2. **환경변수 확인**: 모든 필수 환경변수 설정되었는지 확인
3. **의존성 확인**: `requirements/production.txt` 확인

### **데이터베이스 연결 실패**

1. **Supabase 연결 정보 확인**: URI 형식 확인
2. **방화벽 확인**: Supabase 대시보드 → Settings → Database → Connection Pooling
3. **비밀번호 확인**: Supabase 프로젝트 비밀번호 확인

### **Redis 연결 실패**

1. **Upstash URL 확인**: Redis URL 형식 확인
2. **TLS 설정**: Upstash는 TLS 필수
3. **토큰 확인**: Upstash 토큰 확인

### **CORS 오류**

1. **CORS_ORIGIN 확인**: 프론트엔드 URL과 일치하는지 확인
2. **프로토콜 확인**: `http://` vs `https://` 확인

---

## 📚 **참고 자료**

- [Railway Django 가이드](https://docs.railway.app/guides/django)
- [Supabase Django 가이드](https://supabase.com/docs/guides/getting-started/quickstarts/django)
- [Upstash Redis 가이드](https://docs.upstash.com/redis)
- [Vercel Next.js 가이드](https://vercel.com/docs/frameworks/nextjs)
- [WhiteNoise 문서](https://whitenoise.readthedocs.io/)

---

**마지막 업데이트**: 2025.01.14

