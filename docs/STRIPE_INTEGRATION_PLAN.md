# Stripe 결제 통합 계획

## 목표
글로벌 구독 결제 시스템 구축 (무료/유료 티어)

## Stripe 선택 이유
- ✅ 글로벌 표준 (140개국 지원)
- ✅ 구독 관리 우수
- ✅ 한국 카드 지원 (해외 결제)
- ✅ API 우수
- ✅ 수수료 3.4% + $0.30 (합리적)

## 구독 플랜

### Free Tier
- 가격: $0
- 기능:
  - 기본 재무 지표 (TTM)
  - 메이트 점수 조회
  - 최신 10-K 요약 (1개 종목/월)
  - 종목 비교 (최대 3개)
  - 포트폴리오 (최대 5개 종목)

### Standard Tier
- 가격: $19.99/월 (₩29,000 상당)
- Stripe Product ID: `prod_standard_monthly`
- Price ID: `price_standard_monthly`
- 기능:
  - 모든 Free 기능
  - 500개 종목 전체 접근
  - 과거 5년 10-K/10-Q
  - 포트폴리오 무제한
  - 실시간 리스크 알림
  - 상세 경쟁사 분석

### Premium Tier
- 가격: $49.99/월 (₩69,000 상당)
- Stripe Product ID: `prod_premium_monthly`
- Price ID: `price_premium_monthly`
- 기능:
  - 모든 Standard 기능
  - 증권사 계좌 연동 (Plaid)
  - AI 포트폴리오 추천
  - 백테스트 시뮬레이션
  - API 접근
  - 월간 PDF 리포트

## 기술 구현

### Backend (Django)

#### 1. 모델 추가
```python
# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """커스텀 사용자 모델"""
    
    TIER_CHOICES = [
        ('free', 'Free'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]
    
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='free')
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    subscription_status = models.CharField(max_length=50, blank=True, null=True)  # active, canceled, past_due
    subscription_end_date = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 2. Stripe Webhook 처리
```python
# api/payments/views.py
import stripe
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook(request):
    """Stripe Webhook 핸들러"""
    
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return Response({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return Response({'error': 'Invalid signature'}, status=400)
    
    # 이벤트 타입별 처리
    if event['type'] == 'customer.subscription.created':
        handle_subscription_created(event['data']['object'])
    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event['data']['object'])
    elif event['type'] == 'invoice.payment_succeeded':
        handle_payment_succeeded(event['data']['object'])
    elif event['type'] == 'invoice.payment_failed':
        handle_payment_failed(event['data']['object'])
    
    return Response({'status': 'success'})


def handle_subscription_created(subscription):
    """구독 생성"""
    from apps.users.models import User
    
    user = User.objects.get(stripe_customer_id=subscription['customer'])
    
    # Tier 업그레이드
    price_id = subscription['items']['data'][0]['price']['id']
    
    if price_id == settings.STRIPE_PRICE_STANDARD:
        user.tier = 'standard'
    elif price_id == settings.STRIPE_PRICE_PREMIUM:
        user.tier = 'premium'
    
    user.stripe_subscription_id = subscription['id']
    user.subscription_status = subscription['status']
    user.subscription_end_date = datetime.fromtimestamp(subscription['current_period_end'])
    user.save()
```

#### 3. 권한 체크 데코레이터
```python
# core/decorators.py
from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def require_tier(required_tier):
    """티어 요구 데코레이터"""
    
    tier_hierarchy = {'free': 0, 'standard': 1, 'premium': 2}
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            if not user.is_authenticated:
                return Response(
                    {'error': '로그인이 필요합니다.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            user_tier_level = tier_hierarchy.get(user.tier, 0)
            required_tier_level = tier_hierarchy.get(required_tier, 0)
            
            if user_tier_level < required_tier_level:
                return Response(
                    {
                        'error': f'{required_tier} 티어가 필요합니다.',
                        'current_tier': user.tier,
                        'required_tier': required_tier,
                        'upgrade_url': '/subscribe'
                    },
                    status=status.HTTP_402_PAYMENT_REQUIRED
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


# 사용 예시:
@action(detail=True, methods=['get'])
@require_tier('standard')
def historical_10k(self, request, pk=None):
    """과거 5년 10-K (Standard 이상)"""
    ...
```

### Frontend (Next.js)

```typescript
// src/components/pricing-table.tsx
export function PricingTable() {
  return (
    <div className="grid md:grid-cols-3 gap-6">
      {/* Free */}
      <div className="border rounded-lg p-6">
        <h3>Free</h3>
        <div className="text-4xl font-bold">$0</div>
        <ul>
          <li>✅ 기본 재무 지표</li>
          <li>✅ 메이트 점수</li>
          <li>✅ 최신 10-K 요약 (1개/월)</li>
          <li>❌ 과거 데이터</li>
        </ul>
      </div>
      
      {/* Standard */}
      <div className="border-2 border-blue-500 rounded-lg p-6">
        <h3>Standard</h3>
        <div className="text-4xl font-bold">$19.99<span className="text-sm">/월</span></div>
        <ul>
          <li>✅ 모든 Free 기능</li>
          <li>✅ 500개 종목</li>
          <li>✅ 과거 5년 데이터</li>
          <li>✅ 리스크 알림</li>
        </ul>
        <button onClick={() => handleSubscribe('standard')}>
          구독하기
        </button>
      </div>
      
      {/* Premium */}
      <div className="border rounded-lg p-6 bg-gradient-to-br from-purple-50">
        <h3>Premium</h3>
        <div className="text-4xl font-bold">$49.99<span className="text-sm">/월</span></div>
        <ul>
          <li>✅ 모든 Standard 기능</li>
          <li>✅ 증권사 연동</li>
          <li>✅ AI 포트폴리오 추천</li>
          <li>✅ 백테스트</li>
        </ul>
        <button onClick={() => handleSubscribe('premium')}>
          구독하기
        </button>
      </div>
    </div>
  )
}
```

---

## 🎯 **즉시 실행 가능한 계획:**

### **이번 주 (Week 1):**
```
✅ 15개 종목 DB 임포트 (지금!)
✅ 프론트엔드 UI 확인
✅ 다음 20개 종목 선정
```

### **다음 주 (Week 2):**
```
✅ Stripe 계정 생성
✅ Stripe 통합 (백엔드 + 프론트)
✅ 무료/유료 분리
✅ 20개 추가 종목 분석 (저와 함께)
```

### **Week 3-4:**
```
✅ 100개 종목 완성
✅ 본인 포트폴리오 테스트
✅ 친구/지인 베타 테스트
```

---

**먼저 DB 임포트부터 완료하시겠어요?**

```bash
python scripts/import_ai_analyses.py
```

그 다음 Stripe 통합을 바로 시작하겠습니다! 🚀
