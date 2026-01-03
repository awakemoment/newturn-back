from django.urls import path
from . import views

urlpatterns = [
    path('kakao/login/', views.kakao_login, name='kakao-login'),
    path('google/login/', views.google_login, name='google-login'),
    path('logout/', views.logout, name='logout'),
    path('me/', views.me, name='me'),
]

