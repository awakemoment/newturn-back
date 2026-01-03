from .base import *

# ==================
# 로컬 개발 환경 설정
# ==================

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# CORS 설정 (프론트엔드 로컬 개발)
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# Database - SQLite (로컬 개발용)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 이메일 설정 (로컬 - 콘솔 출력)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 캐시 설정 (로컬 - 메모리)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# 정적 파일
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# 로깅 레벨
LOGGING['root']['level'] = 'DEBUG'

# ==================
# Stripe 설정
# ==================
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_...')  # 실제 키로 교체 필요
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_...')  # 실제 키로 교체 필요
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_...')  # 실제 키로 교체 필요

# Stripe Price ID (Stripe Dashboard에서 생성 후 입력)
STRIPE_PRICE_STANDARD = os.environ.get('STRIPE_PRICE_STANDARD', 'price_standard_monthly')
STRIPE_PRICE_PREMIUM = os.environ.get('STRIPE_PRICE_PREMIUM', 'price_premium_monthly')

# 프론트엔드 URL
FRONTEND_URL = 'http://localhost:3000'

print("=" * 50)
print("🚀 Newturn Backend - LOCAL 환경")
print("=" * 50)
print(f"📍 Backend: http://localhost:8000")
print(f"📍 Admin: http://localhost:8000/admin")
print(f"📍 API Docs: http://localhost:8000/swagger")
print("=" * 50)

