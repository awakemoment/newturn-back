"""
Newturn URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Swagger/API Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Newturn API",
        default_version='v1',
        description="개인 투자자를 위한 AI 분석 메이트 서비스",
        contact=openapi.Contact(email="support@newturn.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API Endpoints
    path('api/users/', include('api.users.urls')),
    path('api/stocks/', include('api.stocks.urls')),
    path('api/analysis/', include('api.analysis.urls')),
    path('api/watchlist/', include('api.watchlist.urls')),
    path('api/portfolio/', include('api.portfolio.urls')),
    path('api/payments/', include('api.payments.urls')),
    path('api/content/', include('api.content.urls')),
    path('api/accounts/', include('api.accounts.urls')),
]

# Static/Media files (로컬 개발용)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

