"""
계좌 관리 API URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryAccountViewSet,
    SavingsRewardViewSet,
    DepositAccountViewSet,
)
from .views_plaid import (
    create_link_token,
    exchange_public_token,
    UserBankAccountViewSet,
)

router = DefaultRouter()
router.register(r'category-accounts', CategoryAccountViewSet, basename='category-account')
router.register(r'savings-rewards', SavingsRewardViewSet, basename='savings-reward')
router.register(r'deposit-accounts', DepositAccountViewSet, basename='deposit-account')
router.register(r'bank-accounts', UserBankAccountViewSet, basename='bank-account')

urlpatterns = [
    path('', include(router.urls)),
    # 예치금 계좌 조회 (단수형)
    path('deposit-account/', DepositAccountViewSet.as_view({'get': 'current'}), name='deposit-account-current'),
    # Plaid 연동
    path('plaid/link-token/', create_link_token, name='plaid-link-token'),
    path('plaid/exchange-token/', exchange_public_token, name='plaid-exchange-token'),
]

