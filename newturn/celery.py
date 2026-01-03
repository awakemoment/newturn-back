"""
Celery 설정

Django 프로젝트와 Celery 통합
"""
import os
from celery import Celery
from django.conf import settings

# Django settings 모듈 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

app = Celery('newturn')

# Django settings에서 Celery 설정 로드
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django 앱에서 tasks 자동 발견
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

