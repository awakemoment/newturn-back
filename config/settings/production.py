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

# CORS 설정 (프론트엔드 배포 도메인)
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

# 이메일 설정 (Gmail SMTP 또는 SendGrid)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@newturn.com')

# Static/Media 파일 - WhiteNoise (Railway 내장)
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
# CompressedStaticFilesStorage: manifest 없이 작동 (collectstatic 없어도 동작)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# WhiteNoise Middleware 추가 (SecurityMiddleware 다음에 추가)
# base.py의 MIDDLEWARE를 상속받아 WhiteNoise 추가
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

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

# Sentry 에러 트래킹
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

# 로깅 레벨
LOGGING['root']['level'] = 'WARNING'

print("=" * 50)
print("🌍 Newturn Backend - PRODUCTION 환경")
print("=" * 50)

