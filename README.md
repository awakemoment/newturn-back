# Newturn Backend

미국 주식 투자를 위한 밸류에이션 도구 및 데이터 분석 플랫폼 백엔드

## 📋 프로젝트 개요

Newturn은 개인 투자자를 위한 밸류에이션 도구와 투자 데이터 분석 플랫폼입니다. 4명의 투자 대가(Graham, Fisher, Greenblatt, Lynch)의 관점으로 종목을 분석하고, 절약→투자 시스템을 통해 실전 투자를 지원합니다.

### 주요 기능
- 📊 **4개 메이트 밸류에이션**: Benjamin, Fisher, Greenblatt, Lynch 관점의 종목 분석
- 💰 **절약→투자 시스템**: 카테고리 통장, 자동 절약, 주식 투자 전환
- 📈 **재무 데이터 분석**: EDGAR API를 통한 실시간 재무 데이터 수집 및 분석
- 🏦 **은행 계좌 연동**: Plaid를 통한 미국 은행 계좌 연결
- 📱 **주식 거래**: Alpaca API를 통한 Paper/Live 트레이딩
- 📚 **콘텐츠 큐레이션**: 투자 관련 콘텐츠 큐레이션 시스템

## 🛠️ 기술 스택

- **Framework**: Django 4.2 LTS
- **API**: Django REST Framework
- **Database**: PostgreSQL (Supabase), SQLite (로컬 개발)
- **Cache/Broker**: Redis (Upstash)
- **Task Queue**: Celery, Celery Beat
- **Authentication**: Token Authentication
- **API Documentation**: drf-yasg (Swagger)

## 🚀 빠른 시작

### 사전 요구사항

- Python 3.11+
- PostgreSQL (프로덕션) 또는 SQLite (로컬 개발)
- Redis (선택사항, Celery 사용 시)

### 설치

1. **저장소 클론**
```bash
git clone https://github.com/awakemoment/newturn-back.git
cd newturn-back
```

2. **가상환경 생성 및 활성화**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **의존성 설치**
```bash
pip install -r requirements/base.txt
pip install -r requirements/production.txt
```

4. **환경변수 설정**
```bash
# .env 파일 생성
cp .env.example .env
# .env 파일 편집 (SECRET_KEY, DATABASE_URL 등)
```

5. **데이터베이스 마이그레이션**
```bash
python manage.py migrate
```

6. **슈퍼유저 생성**
```bash
python manage.py createsuperuser
```

7. **서버 실행**
```bash
python manage.py runserver
```

## 📁 프로젝트 구조

```
newturn-back/
├── api/                    # API 엔드포인트
│   ├── accounts/          # 계좌 관리 (카테고리 통장, 투자)
│   ├── stocks/            # 종목 정보
│   ├── analysis/          # 메이트 분석
│   ├── portfolio/         # 포트폴리오
│   ├── watchlist/         # 관심종목
│   └── content/           # 콘텐츠 큐레이션
├── apps/                   # Django 앱
│   ├── accounts/          # 계좌 모델 및 서비스
│   ├── stocks/            # 종목 모델
│   ├── analysis/          # 분석 모델
│   ├── portfolio/         # 포트폴리오 모델
│   ├── watchlist/         # 관심종목 모델
│   ├── content/           # 콘텐츠 모델
│   └── users/             # 사용자 모델
├── config/                 # Django 설정
│   ├── settings/          # 환경별 설정 (base, local, production)
│   └── wsgi/              # WSGI 설정
├── core/                   # 공통 유틸리티
│   └── utils/             # 밸류에이션 엔진 등
├── scripts/                # 데이터 수집 스크립트
├── requirements/           # Python 패키지 의존성
│   ├── base.txt           # 기본 패키지
│   ├── dev.txt            # 개발 패키지
│   └── production.txt     # 프로덕션 패키지
├── manage.py
└── README.md
```

## 🔧 환경변수 설정

### 로컬 개발 (.env)

```bash
DJANGO_SETTINGS_MODULE=config.settings.local
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database (SQLite 기본값 또는 PostgreSQL)
DATABASE_URL=sqlite:///db.sqlite3
# 또는
DATABASE_URL=postgresql://user:password@localhost:5432/newturn

# Redis (선택사항)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# CORS
CORS_ORIGIN=http://localhost:3000

# API Keys (필요 시)
PLAID_CLIENT_ID=your-plaid-client-id
PLAID_SECRET=your-plaid-secret
ALPACA_API_KEY=your-alpaca-api-key
ALPACA_SECRET_KEY=your-alpaca-secret-key
POLYGON_API_KEY=your-polygon-api-key
```

### 프로덕션 (Railway)

자세한 환경변수 설정은 [RAILWAY_ENV_VARIABLES.md](./RAILWAY_ENV_VARIABLES.md)를 참고하세요.

## 📚 주요 문서

- [배포 가이드](./DEPLOYMENT_GUIDE.md) - Railway + Supabase + Upstash 배포
- [빠른 시작 배포](./DEPLOYMENT_QUICK_START.md) - 배포 빠른 참조
- [마스터 로드맵](./MASTER_ROADMAP.md) - 전체 프로젝트 계획
- [인프라 전략](./INFRASTRUCTURE_STRATEGY.md) - 서버/클라우드 전략
- [데이터 전략](./DATA_BUSINESS_STRATEGY.md) - 데이터 보존 및 판매 전략
- [프로젝트 인덱스](./PROJECT_INDEX.md) - 문서 인덱스

## 🔐 API 인증

대부분의 API는 Token Authentication을 사용합니다.

```bash
# 로그인
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# API 호출 (토큰 사용)
curl -X GET http://localhost:8000/api/stocks/ \
  -H "Authorization: Token your-token-here"
```

## 🧪 개발

### 데이터 수집 스크립트

```bash
# 재무 데이터 수집
python scripts/collect_financial_data.py

# 메이트 점수 계산
python scripts/calculate_mate_scores.py

# 주가 데이터 수집
python scripts/collect_stock_prices.py
```

### 테스트

```bash
python manage.py test
```

## 📦 배포

### Railway 배포

1. Railway 프로젝트 생성
2. GitHub 저장소 연결
3. 환경변수 설정 (RAILWAY_ENV_VARIABLES.md 참고)
4. 자동 배포 완료

자세한 배포 가이드는 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)를 참고하세요.

## 📊 데이터베이스

- **로컬 개발**: SQLite (db.sqlite3)
- **프로덕션**: PostgreSQL (Supabase)

### 마이그레이션

```bash
# 마이그레이션 생성
python manage.py makemigrations

# 마이그레이션 적용
python manage.py migrate
```

## 🔄 Celery 작업

백그라운드 작업은 Celery를 사용합니다.

```bash
# Celery Worker 실행
celery -A newturn worker -l info

# Celery Beat 실행 (스케줄링)
celery -A newturn beat -l info
```

## 📝 라이센스

Private - All Rights Reserved

## 👥 팀

- 개발: awakemoment

## 📞 문의

이슈는 GitHub Issues를 통해 제출해주세요.

---

**마지막 업데이트**: 2025.01.14
