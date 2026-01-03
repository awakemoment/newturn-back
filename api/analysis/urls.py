from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'journals', views.ValuationJournalEntryViewSet, basename='valuation-journal')
router.register(r'', views.AnalysisViewSet, basename='analysis')

urlpatterns = [
    path('', include(router.urls)),
]

