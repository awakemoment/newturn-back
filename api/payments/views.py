"""
Stripe 결제 API
"""
try:
    import stripe
except ImportError:
    stripe = None
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from datetime import datetime

from apps.users.models import User


# Stripe API 키 설정
if stripe:
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    if not stripe:
        return Response(
            {'error': 'Stripe is not installed.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    """
    Stripe Checkout 세션 생성
    
    POST /api/payments/create-checkout/
    {
        "tier": "standard" | "premium"
    }
    """
    tier = request.data.get('tier')
    
    if tier not in ['standard', 'premium']:
        return Response(
            {'error': 'Invalid tier. Must be "standard" or "premium".'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = request.user
    
    # Stripe Customer 생성 또는 가져오기
    if user.stripe_customer_id:
        customer_id = user.stripe_customer_id
    else:
        customer = stripe.Customer.create(
            email=user.email,
            metadata={
                'user_id': user.id,
                'username': user.username
            }
        )
        user.stripe_customer_id = customer.id
        user.save()
        customer_id = customer.id
    
    # Price ID 매핑
    price_ids = {
        'standard': settings.STRIPE_PRICE_STANDARD,
        'premium': settings.STRIPE_PRICE_PREMIUM,
    }
    
    try:
        # Checkout Session 생성
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            mode='subscription',
            payment_method_types=['card'],
            line_items=[{
                'price': price_ids[tier],
                'quantity': 1,
            }],
            success_url=f"{settings.FRONTEND_URL}/subscribe/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/subscribe/cancel",
            metadata={
                'user_id': user.id,
                'tier': tier
            }
        )
        
        return Response({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_portal_session(request):
    if not stripe:
        return Response(
            {'error': 'Stripe is not installed.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    """
    Stripe Customer Portal 세션 생성 (구독 관리)
    
    POST /api/payments/create-portal/
    """
    user = request.user
    
    if not user.stripe_customer_id:
        return Response(
            {'error': 'No Stripe customer found.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=f"{settings.FRONTEND_URL}/settings",
        )
        
        return Response({
            'portal_url': portal_session.url
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook(request):
    if not stripe:
        return Response(
            {'error': 'Stripe is not installed.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    """
    Stripe Webhook 핸들러
    
    POST /api/payments/webhook/
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return Response({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return Response({'error': 'Invalid signature'}, status=400)
    
    # 이벤트 타입별 처리
    event_type = event['type']
    
    if event_type == 'customer.subscription.created':
        handle_subscription_created(event['data']['object'])
    elif event_type == 'customer.subscription.updated':
        handle_subscription_updated(event['data']['object'])
    elif event_type == 'customer.subscription.deleted':
        handle_subscription_deleted(event['data']['object'])
    elif event_type == 'invoice.payment_succeeded':
        handle_payment_succeeded(event['data']['object'])
    elif event_type == 'invoice.payment_failed':
        handle_payment_failed(event['data']['object'])
    
    return Response({'status': 'success'})


def handle_subscription_created(subscription):
    """구독 생성 처리"""
    customer_id = subscription['customer']
    
    try:
        user = User.objects.get(stripe_customer_id=customer_id)
    except User.DoesNotExist:
        print(f"User not found for customer {customer_id}")
        return
    
    # Price ID로 티어 결정
    price_id = subscription['items']['data'][0]['price']['id']
    
    if price_id == settings.STRIPE_PRICE_STANDARD:
        user.membership_tier = 'standard'
    elif price_id == settings.STRIPE_PRICE_PREMIUM:
        user.membership_tier = 'premium'
    
    user.stripe_subscription_id = subscription['id']
    user.subscription_status = subscription['status']
    user.membership_started_at = datetime.fromtimestamp(subscription['current_period_start'])
    user.membership_expires_at = datetime.fromtimestamp(subscription['current_period_end'])
    user.save()
    
    print(f"✅ Subscription created for {user.email}: {user.membership_tier}")


def handle_subscription_updated(subscription):
    """구독 업데이트 처리"""
    customer_id = subscription['customer']
    
    try:
        user = User.objects.get(stripe_customer_id=customer_id)
    except User.DoesNotExist:
        print(f"User not found for customer {customer_id}")
        return
    
    user.subscription_status = subscription['status']
    user.membership_expires_at = datetime.fromtimestamp(subscription['current_period_end'])
    
    # 취소된 경우
    if subscription['status'] == 'canceled':
        user.membership_tier = 'free'
        user.stripe_subscription_id = None
    
    user.save()
    
    print(f"✅ Subscription updated for {user.email}: {user.subscription_status}")


def handle_subscription_deleted(subscription):
    """구독 삭제 처리"""
    customer_id = subscription['customer']
    
    try:
        user = User.objects.get(stripe_customer_id=customer_id)
    except User.DoesNotExist:
        print(f"User not found for customer {customer_id}")
        return
    
    user.membership_tier = 'free'
    user.stripe_subscription_id = None
    user.subscription_status = 'canceled'
    user.save()
    
    print(f"✅ Subscription deleted for {user.email}")


def handle_payment_succeeded(invoice):
    """결제 성공 처리"""
    customer_id = invoice['customer']
    
    try:
        user = User.objects.get(stripe_customer_id=customer_id)
        print(f"✅ Payment succeeded for {user.email}: ${invoice['amount_paid']/100}")
    except User.DoesNotExist:
        print(f"User not found for customer {customer_id}")


def handle_payment_failed(invoice):
    """결제 실패 처리"""
    customer_id = invoice['customer']
    
    try:
        user = User.objects.get(stripe_customer_id=customer_id)
        user.subscription_status = 'past_due'
        user.save()
        print(f"⚠️ Payment failed for {user.email}")
        # TODO: 이메일 알림
    except User.DoesNotExist:
        print(f"User not found for customer {customer_id}")

