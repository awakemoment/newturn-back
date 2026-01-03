from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    사용자 모델
    jgabin의 User 모델 구조 참고
    """
    email = models.EmailField('이메일', unique=True)
    phone = models.CharField('휴대폰', max_length=20, blank=True, null=True)
    
    # 소셜 로그인
    social_provider = models.CharField('소셜 제공자', max_length=20, blank=True, null=True)  # kakao, google
    social_id = models.CharField('소셜 ID', max_length=100, blank=True, null=True)
    
    # 메타데이터
    created_at = models.DateTimeField('가입일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    last_login_at = models.DateTimeField('마지막 로그인', null=True, blank=True)
    
    # 멤버십
    membership_tier = models.CharField(
        '멤버십 등급',
        max_length=20,
        choices=[
            ('free', 'Free'),
            ('standard', 'Standard'),  # $19.99/월
            ('premium', 'Premium'),    # $49.99/월
        ],
        default='free'
    )
    membership_started_at = models.DateTimeField('멤버십 시작일', null=True, blank=True)
    membership_expires_at = models.DateTimeField('멤버십 만료일', null=True, blank=True)
    
    # Stripe 결제
    stripe_customer_id = models.CharField('Stripe 고객 ID', max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField('Stripe 구독 ID', max_length=255, blank=True, null=True)
    subscription_status = models.CharField(
        '구독 상태',
        max_length=50,
        blank=True,
        null=True,
        help_text='active, canceled, past_due, etc.'
    )
    
    # 추천 메이트
    recommended_mate = models.CharField('추천 메이트', max_length=50, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = '사용자'
        verbose_name_plural = '사용자'
    
    def __str__(self):
        return f"{self.email} ({self.get_membership_tier_display()})"

