"""
계좌 API 테스트 스크립트
"""
import os
import sys
import django

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import CategoryAccount, Transaction, SavingsReward, DepositAccount
from apps.stocks.models import Stock
from decimal import Decimal

User = get_user_model()

def test_accounts_api():
    """계좌 API 테스트"""
    print("=" * 60)
    print("계좌 API 테스트")
    print("=" * 60)
    
    # 1. 테스트 사용자 생성 또는 가져오기
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'password': 'pbkdf2_sha256$...'  # 실제로는 해시된 비밀번호
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✅ 테스트 사용자 생성: {user.username}")
    else:
        print(f"✅ 기존 사용자 사용: {user.username}")
    
    # 2. 카테고리 통장 생성
    account, created = CategoryAccount.objects.get_or_create(
        user=user,
        category='coffee',
        defaults={
            'name': '카페/베이커리 통장',
            'monthly_budget': Decimal('100.00'),
        }
    )
    if created:
        print(f"✅ 카테고리 통장 생성: {account.name}")
    else:
        print(f"✅ 기존 통장 사용: {account.name}")
    
    # 3. 입금 테스트
    account.balance += Decimal('100.00')
    account.total_deposited += Decimal('100.00')
    account.save()
    
    Transaction.objects.create(
        account=account,
        transaction_type='deposit',
        amount=Decimal('100.00'),
        balance_after=account.balance,
        note='테스트 입금'
    )
    print(f"✅ 입금 테스트: $100.00")
    
    # 4. 출금 테스트
    account.balance -= Decimal('30.00')
    account.current_month_spent += Decimal('30.00')
    account.save()
    
    Transaction.objects.create(
        account=account,
        transaction_type='withdrawal',
        amount=Decimal('30.00'),
        balance_after=account.balance,
        merchant_name='스타벅스',
        category_detail='아메리카노',
        note='커피 구매'
    )
    print(f"✅ 출금 테스트: $30.00")
    
    # 5. 절약 금액 계산
    savings = account.calculate_monthly_savings()
    print(f"✅ 절약 금액: ${savings}")
    
    # 6. 예치금 계좌 생성
    deposit_account, created = DepositAccount.objects.get_or_create(
        user=user,
        defaults={
            'account_number': f'DEP-{user.id}',
            'balance': Decimal('1000.00'),
        }
    )
    if created:
        print(f"✅ 예치금 계좌 생성: {deposit_account.account_number}")
    else:
        print(f"✅ 기존 예치금 계좌 사용: {deposit_account.account_number}")
    
    # 7. 종목 확인 (NVDA)
    try:
        stock = Stock.objects.get(stock_code='NVDA')
        print(f"✅ 종목 확인: {stock.stock_code} - {stock.stock_name}")
        
        # 8. 투자 테스트 (절약 금액이 있을 때만)
        if savings > 0:
            print(f"\n💡 절약 금액 ${savings}으로 {stock.stock_code} 투자 가능")
            print("   (실제 투자는 API를 통해 진행하세요)")
    except Stock.DoesNotExist:
        print("⚠️ NVDA 종목이 없습니다. 종목을 먼저 추가하세요.")
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)
    print(f"\n📊 통장 정보:")
    print(f"   - 통장명: {account.name}")
    print(f"   - 잔액: ${account.balance}")
    print(f"   - 월 예산: ${account.monthly_budget}")
    print(f"   - 이번 달 사용: ${account.current_month_spent}")
    print(f"   - 절약: ${savings}")
    print(f"\n💰 예치금 계좌:")
    print(f"   - 계좌번호: {deposit_account.account_number}")
    print(f"   - 잔액: ${deposit_account.balance}")
    print(f"\n🔗 API 테스트:")
    print(f"   - 통장 목록: GET /api/accounts/category-accounts/")
    print(f"   - 통장 상세: GET /api/accounts/category-accounts/{account.id}/")
    print(f"   - 절약 계산: GET /api/accounts/category-accounts/{account.id}/monthly-savings/")
    print(f"   - 투자: POST /api/accounts/category-accounts/{account.id}/invest-savings/")

if __name__ == '__main__':
    test_accounts_api()

