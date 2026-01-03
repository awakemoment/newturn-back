"""
커스텀 권한 체크
"""
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from functools import wraps


def require_tier(required_tier):
    """
    티어 요구 데코레이터
    
    사용 예:
    @action(detail=True, methods=['get'])
    @require_tier('standard')
    def historical_analysis(self, request, pk=None):
        ...
    """
    
    tier_hierarchy = {
        'free': 0,
        'standard': 1,
        'premium': 2,
    }
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            user = request.user
            
            if not user.is_authenticated:
                return Response(
                    {'error': '로그인이 필요합니다.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            user_tier_level = tier_hierarchy.get(user.membership_tier, 0)
            required_tier_level = tier_hierarchy.get(required_tier, 0)
            
            if user_tier_level < required_tier_level:
                return Response(
                    {
                        'error': f'{required_tier.capitalize()} 티어가 필요합니다.',
                        'current_tier': user.membership_tier,
                        'required_tier': required_tier,
                        'upgrade_url': '/subscribe',
                        'message': f'{required_tier.capitalize()} 구독으로 업그레이드하여 이 기능을 이용하세요.'
                    },
                    status=status.HTTP_402_PAYMENT_REQUIRED
                )
            
            return view_func(self, request, *args, **kwargs)
        
        return wrapper
    return decorator


class IsPremiumUser(permissions.BasePermission):
    """Premium 티어 사용자만 허용"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.membership_tier == 'premium'


class IsStandardOrPremium(permissions.BasePermission):
    """Standard 또는 Premium 티어 사용자만 허용"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.membership_tier in ['standard', 'premium']

