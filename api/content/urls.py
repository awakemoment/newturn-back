from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContentViewSet, WeeklyBriefViewSet

app_name = 'content'

router = DefaultRouter()
router.register(r'contents', ContentViewSet, basename='content')
router.register(r'weekly-briefs', WeeklyBriefViewSet, basename='weekly-brief')

urlpatterns = [
    path('', include(router.urls)),
]

