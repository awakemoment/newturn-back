import datetime
from environ import Env
import os
from os import environ
from os.path import join
import logging
from pathlib import Path


# ==========
# Django 설정
# ==========
DEBUG = True
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = Env()
Env.read_env(
    env_file=os.path.join(BASE_DIR, '.env')
)

SECRET_KEY = env('SECRET_KEY', default='django-insecure-please-change-in-production')
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
ALLOWED_HOSTS = ['*']
APPEND_SLASH = True
ROOT_URLCONF = 'newturn.urls'
WSGI_APPLICATION = 'config.wsgi.base.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ============
# 사용자 인증 설정
# ============
AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)
ACCOUNT_EMAIL_REQUIRED = True


# =============
# Django 앱 설정
# =============
DJANGO_APPS = (
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

# Jazzmin (모던 Admin UI)
try:
    import jazzmin
    DJANGO_APPS = ('jazzmin',) + DJANGO_APPS
    JAZZMIN_SETTINGS = {
        'site_title': 'Newturn Admin',
        'site_header': 'Newturn 관리',
        'site_brand': 'Newturn',
        'welcome_sign': '관리 대시보드',
        'show_ui_builder': False,
    }
except Exception:
    pass

THIRD_PARTY_APPS = (
    'django_extensions',
    'django_celery_beat',
    'django_celery_results',
    'drf_yasg',
    'rest_framework',
    'rest_framework.authtoken',
)

PROJECT_APPS = (
    'apps.users',
    'apps.stocks',
    'apps.analysis',
    'apps.watchlist',
    'apps.portfolio',
    'apps.content',  # 콘텐츠 큐레이션
    'apps.accounts',  # 계좌 관리 (카테고리 통장, 절약→투자)
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS


# ================
# Middleware 설정
# ================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ================
# Database 설정
# ================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ========================
# REST Framework 설정
# ========================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        # SessionAuthentication 제거 (CSRF 이슈)
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',  # 기본 AllowAny (나중에 인증 추가)
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    # 'EXCEPTION_HANDLER': 'core.utils.error_handler.custom_exception_handler',  # 주석처리 (모듈 없음)
}


# ============
# CORS 설정
# ============
CORS_ALLOWED_ORIGINS = [
    env('CORS_ORIGIN', default='http://localhost:3000'),
]
CORS_ALLOW_CREDENTIALS = True


# ===================
# 국제화 및 시간대 설정
# ===================
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_L10N = True
USE_TZ = False  # 한국 시간 사용


# ==============
# Static 파일 설정
# ==============
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ===================
# 템플릿 설정
# ===================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ============
# OpenAI 설정
# ============
OPENAI_API_KEY = env('OPENAI_API_KEY', default='')
OPENAI_MODEL = env('OPENAI_MODEL', default='gpt-4-turbo-preview')


# ===========
# 미국 주식 데이터 API 설정
# ===========
# EDGAR (SEC) - 재무제표
# yfinance - 주가 데이터
EDGAR_USER_AGENT = env('EDGAR_USER_AGENT', default='Newturn support@newturn.com')
ALPHA_VANTAGE_KEY = env('ALPHA_VANTAGE_KEY', default='')  # 선택


# ==============
# Celery 설정
# ==============
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Celery Beat 스케줄 (주가 업데이트)
from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'update-reward-prices-daily': {
        'task': 'accounts.update_reward_prices',
        'schedule': crontab(hour=18, minute=0),  # 매일 오후 6시 (미국 시장 마감 후)
        'options': {'timezone': TIME_ZONE},
    },
}


# =============
# 로깅 설정
# =============
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'newturn.log'),
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}


# =============
# 기타 설정
# =============
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SITE_ID = 1

