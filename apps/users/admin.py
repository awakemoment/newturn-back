from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'membership_tier', 'created_at', 'is_active']
    list_filter = ['membership_tier', 'is_active', 'created_at']
    search_fields = ['email', 'username']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('소셜 로그인', {'fields': ('social_provider', 'social_id')}),
        ('멤버십', {'fields': ('membership_tier', 'membership_started_at', 'membership_expires_at')}),
        ('메이트', {'fields': ('recommended_mate',)}),
    )

