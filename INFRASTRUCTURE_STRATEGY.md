# 🏗️ Newturn 인프라 전략 (비용 최소화)

**작성일**: 2025.01.14  
**목적**: 서버 호스팅, 클라우드 선택, 전체 인프라 아키텍처 전략

---

## 🎯 **전체 아키텍처**

```
┌─────────────────┐
│   Frontend      │
│   (Next.js)     │
│   Vercel        │
│   $0/월         │
└────────┬────────┘
         │ HTTPS
         │
┌────────▼────────┐
│   Backend       │
│   (Django)      │
│   Railway/Render│
│   $0-5/월       │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│ DB    │ │ Redis │
│(PostgreSQL)│ │(Celery) │
│Supabase│ │Upstash│
│$0-25/월│ │$0/월 │
└───────┘ └───────┘
```

---

## 🖥️ **프론트엔드 호스팅**

### **Vercel (추천)** ⭐⭐⭐⭐⭐

**특징:**
- Next.js 공식 호스팅 플랫폼
- 무료 티어 제공
- 자동 배포 (Git 연동)
- CDN, SSL 자동 제공
- 글로벌 엣지 네트워크

**무료 티어:**
- 100GB 대역폭/월
- 무제한 요청
- SSL 인증서 자동
- Git 연동 무제한

**비용:**
- **무료 티어**: $0/월 (개인 프로젝트)
- **Pro**: $20/월 (팀, 더 많은 기능)

**장점:**
- ✅ Next.js 최적화
- ✅ 배포 자동화
- ✅ CDN 제공
- ✅ SSL 자동

**단점:**
- ⚠️ 서버리스 함수 실행 시간 제한 (무료: 10초)

**배포:**
```bash
# Vercel CLI 설치
npm i -g vercel

# 배포
vercel

# 프로덕션 배포
vercel --prod
```

---

## 🔧 **백엔드 호스팅**

### **Option 1: Railway (추천 - MVP 단계)** ⭐⭐⭐⭐⭐

**특징:**
- 간단한 설정
- Git 연동 자동 배포
- PostgreSQL, Redis 통합 제공
- 무료 티어 (제한적)

**무료 티어:**
- $5 크레딧/월 (자동 소진)
- 약 500시간 실행 시간 (프리티어 서버 기준)
- PostgreSQL 포함
- Redis 별도 ($5/월 또는 Upstash 무료)

**유료 플랜:**
- **Starter**: $5/월 (기본 서버)
- **Developer**: $20/월 (더 많은 리소스)

**장점:**
- ✅ 설정 간단
- ✅ Git 자동 배포
- ✅ PostgreSQL 통합
- ✅ 로그 확인 쉬움
- ✅ 환경변수 관리 편리

**단점:**
- ⚠️ 무료 티어 제한적
- ⚠️ 트래픽 제한 (무료 티어)

**비용 예상:**
- 서버: $5/월 (Starter 플랜)
- PostgreSQL: 포함 (또는 Supabase 무료)
- Redis: $0/월 (Upstash 무료) 또는 $5/월 (Railway)
- **총: $5-10/월**

---

### **Option 2: Render (대안)** ⭐⭐⭐⭐

**특징:**
- 무료 티어 제공 (제한적)
- Git 연동
- PostgreSQL, Redis 제공
- 자동 SSL

**무료 티어:**
- 서버: 750시간/월 (약 31일)
- PostgreSQL: 90일 무료 (이후 $7/월)
- Redis: $7/월 (무료 없음)

**유료 플랜:**
- **Starter**: $7/월 (서버)
- **Standard**: $25/월 (더 많은 리소스)

**장점:**
- ✅ 무료 티어 제공
- ✅ Git 자동 배포
- ✅ SSL 자동

**단점:**
- ⚠️ 무료 티어 제한적 (서버 750시간/월)
- ⚠️ PostgreSQL 무료 기간 제한 (90일)

**비용 예상:**
- 서버: $0-7/월 (무료 티어 또는 Starter)
- PostgreSQL: $0-7/월 (90일 무료 후 $7/월)
- Redis: $7/월 (Railway보다 비쌈)
- **총: $0-21/월**

---

### **Option 3: Fly.io (경쟁력 있음)** ⭐⭐⭐⭐

**특징:**
- 무료 티어 제공
- 글로벌 배포 (여러 리전)
- PostgreSQL, Redis 제공
- Docker 기반

**무료 티어:**
- 서버: 3개 앱, 256MB RAM/앱
- PostgreSQL: 3GB 스토리지
- Redis: 25MB

**장점:**
- ✅ 무료 티어 제공
- ✅ 글로벌 배포
- ✅ PostgreSQL 무료

**단점:**
- ⚠️ Docker 필요
- ⚠️ 설정이 복잡할 수 있음

**비용 예상:**
- 서버: $0/월 (무료 티어)
- PostgreSQL: $0/월 (무료 티어)
- Redis: $0/월 (무료 티어)
- **총: $0/월** (무료 티어)

---

### **Option 4: AWS (확장 시)** ⭐⭐⭐

**특징:**
- 엔터프라이즈급 안정성
- 확장성
- 복잡한 설정
- 비용 예측 어려움

**구성:**
- EC2: $5-15/월 (t3.micro)
- RDS: $15-30/월 (PostgreSQL)
- ElastiCache: $15/월 (Redis)
- Route 53: $0.50/월 (도메인)
- CloudFront: 사용량 기반

**장점:**
- ✅ 안정성
- ✅ 확장성
- ✅ 전 세계 인프라

**단점:**
- ❌ 비용 높음 (~$50-100/월)
- ❌ 설정 복잡
- ❌ 초기 설정 시간 소요

**비용 예상: $50-100/월**

---

## 🗄️ **데이터베이스 전략**

### **Option 1: Supabase (추천 - MVP)** ⭐⭐⭐⭐⭐

**특징:**
- PostgreSQL 관리형 서비스
- 무료 티어 제공
- 자동 백업
- 대시보드 제공
- REST API 자동 생성

**무료 티어:**
- 500MB 데이터베이스
- 2GB 백업 (7일)
- 자동 백업
- 대시보드

**Pro 플랜:**
- $25/월 (8GB 데이터베이스)
- 7일 Point-in-Time Recovery

**장점:**
- ✅ 무료 티어
- ✅ 자동 백업
- ✅ 대시보드
- ✅ 설정 간단

**비용: $0-25/월**

---

### **Option 2: Railway PostgreSQL**

**특징:**
- Railway에 통합
- 간단한 설정
- 자동 백업

**비용:**
- Starter: 포함 (또는 별도 $5/월)
- 더 큰 플랜: 별도 구독

---

### **Option 3: Render PostgreSQL**

**비용:**
- 90일 무료
- 이후 $7/월

---

## 🔴 **Redis (Celery Broker) 전략**

### **Option 1: Upstash Redis (무료 티어 - 추천)** ⭐⭐⭐⭐⭐

**특징:**
- 서버리스 Redis
- 무료 티어 제공
- REST API 지원

**무료 티어:**
- 10,000 commands/day
- 256MB 스토리지
- 글로벌 리전

**장점:**
- ✅ 무료 티어
- ✅ 서버리스 (비용 효율)
- ✅ Celery와 호환

**비용: $0/월** (무료 티어 충분)

---

### **Option 2: Railway Redis**

**비용: $5/월** (512MB)

---

### **Option 3: Redis 없이 (Cron Job)**

**구성:**
- Celery 대신 Cron Job 사용
- Redis 불필요

**비용: $0/월**

---

## 📊 **비용 비교표**

| 구성 | 프론트엔드 | 백엔드 | DB | Redis | **총 비용** |
|------|------------|--------|----|----|-----------|
| **최소 (무료)** | Vercel ($0) | Fly.io ($0) | Fly.io ($0) | Cron Job ($0) | **$0/월** |
| **권장 (MVP)** | Vercel ($0) | Railway ($5) | Supabase ($0) | Upstash ($0) | **$5/월** |
| **안정 (중간)** | Vercel ($0) | Railway ($5) | Supabase ($25) | Upstash ($0) | **$30/월** |
| **확장 (Pro)** | Vercel ($20) | Railway ($20) | AWS RDS ($30) | AWS ($15) | **$85/월** |

---

## 🎯 **단계별 인프라 전략**

### **Phase 0A-0B: MVP (무료/저비용)** ⭐⭐⭐⭐⭐

**구성:**
```
Frontend: Vercel (무료)
Backend: Fly.io (무료) 또는 Railway ($5/월)
Database: Supabase (무료) 또는 Fly.io PostgreSQL (무료)
Redis: Upstash (무료) 또는 Cron Job (무료)
```

**비용: $0-5/월**

**장점:**
- ✅ 비용 최소화
- ✅ 빠른 시작
- ✅ 충분한 성능 (MVP 단계)

---

### **Phase 1: 성장 (안정성)** ⭐⭐⭐⭐

**구성:**
```
Frontend: Vercel (무료 또는 Pro $20/월)
Backend: Railway ($5-20/월)
Database: Supabase Pro ($25/월)
Redis: Upstash (무료)
```

**비용: $30-50/월**

**장점:**
- ✅ 안정적인 인프라
- ✅ 자동 백업
- ✅ 확장 가능

---

### **Phase 2: 확장 (엔터프라이즈)** ⭐⭐⭐

**구성:**
```
Frontend: Vercel Pro ($20/월)
Backend: AWS (ELB + EC2) ($50/월)
Database: AWS RDS Multi-AZ ($100/월)
Redis: AWS ElastiCache ($30/월)
CDN: CloudFront ($10/월)
```

**비용: $200-300/월**

---

## 🚀 **권장 구현 방안 (Phase 0A-0B)**

### **구성 1: 최소 비용 ($0/월)**

```
Frontend: Vercel (무료)
Backend: Fly.io (무료)
Database: Fly.io PostgreSQL (무료)
Redis: Cron Job (무료, Redis 불필요)
```

**구현:**
1. Vercel에 Next.js 배포
2. Fly.io에 Django 배포
3. Fly.io PostgreSQL 사용
4. Cron Job으로 스케줄링

**비용: $0/월**

---

### **구성 2: 권장 구성 ($5/월)** ⭐⭐⭐⭐⭐

```
Frontend: Vercel (무료)
Backend: Railway ($5/월)
Database: Supabase (무료)
Redis: Upstash (무료)
```

**구현:**
1. Vercel에 Next.js 배포
2. Railway에 Django 배포
3. Supabase PostgreSQL 연결
4. Upstash Redis 연결
5. Celery + Celery Beat 사용

**비용: $5/월**

**장점:**
- ✅ 비용 효율적
- ✅ 안정적
- ✅ 확장 가능
- ✅ 관리 편리

---

## 📋 **배포 체크리스트**

### **1. 도메인 설정**

**옵션:**
- 무료: `.vercel.app`, `.railway.app`
- 유료: 커스텀 도메인 ($10-15/년)

**설정:**
```
프론트엔드: newturn.com (또는 newturn.vercel.app)
백엔드: api.newturn.com (또는 newturn-production.railway.app)
```

---

### **2. 환경변수 설정**

**프론트엔드 (Vercel):**
```
NEXT_PUBLIC_API_URL=https://api.newturn.com
```

**백엔드 (Railway/Fly.io):**
```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=...
ALLOWED_HOSTS=api.newturn.com
CORS_ALLOWED_ORIGINS=https://newturn.com
```

---

### **3. SSL/HTTPS**

- ✅ Vercel: 자동 SSL
- ✅ Railway: 자동 SSL
- ✅ Fly.io: 자동 SSL
- ✅ Render: 자동 SSL

**추가 설정 불필요**

---

### **4. 데이터베이스 마이그레이션**

```bash
# 프로덕션 DB 마이그레이션
python manage.py migrate

# 초기 데이터 로드 (선택)
python manage.py loaddata initial_data.json
```

---

### **5. 스태틱 파일**

**옵션:**
- Vercel: 자동 처리
- Railway/Fly.io: WhiteNoise 또는 S3

---

## 🔐 **보안 설정**

### **프로덕션 설정 (config/settings/production.py)**

```python
# 이미 구현됨
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## 📈 **모니터링 및 로깅**

### **무료 옵션**

**Railway:**
- 로그 자동 수집
- 실시간 로그 확인

**Vercel:**
- Analytics (무료 티어)
- 로그 확인

**추가 (선택):**
- Sentry (에러 트래킹, 무료 티어)
- Logtail (로그 집계, 무료 티어)

---

## 💰 **총 비용 요약**

### **Phase 0A-0B (MVP)**
```
최소 구성: $0/월
권장 구성: $5/월
```

### **Phase 1 (성장)**
```
안정 구성: $30-50/월
```

### **Phase 2 (확장)**
```
엔터프라이즈: $200-300/월
```

---

## 🎯 **최종 권장사항**

### **즉시 구현 (Phase 0A-0B): 권장 구성**

```
✅ Frontend: Vercel (무료)
✅ Backend: Railway ($5/월)
✅ Database: Supabase (무료)
✅ Redis: Upstash (무료)
✅ 총 비용: $5/월
```

**이유:**
1. ✅ 비용 효율적 ($5/월)
2. ✅ 설정 간단
3. ✅ 안정적
4. ✅ 확장 가능
5. ✅ 관리 편리

---

## 📚 **배포 가이드 링크**

### **Vercel**
- [Next.js 배포 가이드](https://vercel.com/docs/frameworks/nextjs)
- 무료 티어 충분

### **Railway**
- [Django 배포 가이드](https://docs.railway.app/guides/django)
- Git 연동 자동 배포

### **Fly.io**
- [Django 배포 가이드](https://fly.io/docs/django/)
- Docker 필요

### **Supabase**
- [Django 연결 가이드](https://supabase.com/docs/guides/getting-started/quickstarts/django)
- PostgreSQL 호환

---

## ⚙️ **현재 프로덕션 설정 (production.py)**

현재 `config/settings/production.py`는 **AWS 기반**으로 설정되어 있습니다:

```python
ALLOWED_HOSTS = [
    'api.newturn.com',
    '.amazonaws.com',
    '.elasticbeanstalk.com',
]

# Database - PostgreSQL (AWS RDS)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        ...
    }
}

# AWS S3 (Static/Media 파일)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'

# Redis (Celery)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://localhost:6379/0'),
    }
}
```

**권장사항:**
- Phase 0A-0B (MVP): `production.py`를 Railway/Supabase/Upstash 기반으로 수정
- Phase 2 (확장): 현재 AWS 설정 유지 또는 Railway → AWS 마이그레이션

---

## 🔄 **마이그레이션 전략**

### **Option A: Railway/Supabase/Upstash로 시작 (권장)**

**수정 필요:**
1. `production.py`에서 AWS S3 제거 (WhiteNoise 또는 Railway Static Files 사용)
2. RDS → Supabase PostgreSQL 변경
3. ElastiCache → Upstash Redis 변경
4. Elastic Beanstalk → Railway 변경

**새로운 설정:**
```python
# config/settings/production.py (Railway 버전)
ALLOWED_HOSTS = [
    'api.newturn.com',
    '.railway.app',  # Railway 도메인
]

# Database - Supabase PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DATABASE_URL'),  # Supabase 연결 문자열
    }
}

# Static Files - WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Redis - Upstash
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL'),  # Upstash 연결 문자열
    }
}
```

---

### **Option B: AWS 유지 (확장 단계)**

현재 `production.py` 설정 유지:
- AWS RDS (PostgreSQL)
- AWS S3 (Static/Media)
- AWS ElastiCache (Redis)
- AWS Elastic Beanstalk (또는 EC2)

**비용:** $50-100/월

---

## 🎯 **최종 권장사항 (업데이트)**

### **Phase 0A-0B (즉시): Railway/Supabase/Upstash**

```
✅ Frontend: Vercel (무료)
✅ Backend: Railway ($5/월)
✅ Database: Supabase (무료)
✅ Redis: Upstash (무료)
✅ Static Files: WhiteNoise (Railway 내장)
✅ 총 비용: $5/월
```

**필요 작업:**
1. `production.py` 수정 (AWS → Railway/Supabase/Upstash)
2. Railway 프로젝트 생성 및 배포
3. Supabase 프로젝트 생성 및 연결
4. Upstash Redis 생성 및 연결
5. Vercel에 프론트엔드 배포

---

### **Phase 2 (확장): AWS**

```
✅ Frontend: Vercel Pro ($20/월)
✅ Backend: AWS EC2/Elastic Beanstalk ($50/월)
✅ Database: AWS RDS ($30/월)
✅ Redis: AWS ElastiCache ($15/월)
✅ Storage: AWS S3 ($5/월)
✅ 총 비용: $120/월
```

**필요 작업:**
- 현재 `production.py` 설정 유지
- AWS 리소스 생성 및 배포

---

**마지막 업데이트**: 2025.01.14

