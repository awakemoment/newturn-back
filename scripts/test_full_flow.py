"""
전체 플로우 통합 테스트

1. 통장 생성
2. 입금
3. 출금
4. 절약 계산
5. 투자 실행
6. 주가 업데이트
7. 매도 (수익일 때)
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import CategoryAccount, Transaction, SavingsReward, DepositAccount
from apps.accounts.services.trading_service import TradingService
from apps.stocks.models import Stock, StockPrice
from decimal import Decimal
from django.utils import timezone
from datetime import date, timedelta

User = get_user_model()

def test_full_flow():
    """전체 플로우 테스트"""
    print("=" * 60)
    print("전체 플로우 통합 테스트")
    print("=" * 60)
    
    # 1. 테스트 사용자
    user, _ = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if user.password == '':
        user.set_password('testpass123')
        user.save()
    print(f"✅ 사용자: {user.username}")
    
    # 2. 카테고리 통장 생성
    account, _ = CategoryAccount.objects.get_or_create(
        user=user,
        category='coffee',
        defaults={
            'name': '카페/베이커리 통장',
            'monthly_budget': Decimal('100.00'),
        }
    )
    print(f"✅ 통장: {account.name}")
    
    # 3. 입금
    account.balance = Decimal('100.00')
    account.total_deposited = Decimal('100.00')
    account.save()
    print(f"✅ 입금: $100.00")
    
    # 4. 출금 (소비)
    account.balance -= Decimal('30.00')
    account.current_month_spent = Decimal('30.00')
    account.save()
    print(f"✅ 출금: $30.00 (커피 구매)")
    
    # 5. 절약 계산
    savings = account.calculate_monthly_savings()
    print(f"✅ 절약 금액: ${savings}")
    
    # 6. 예치금 계좌
    deposit_account, _ = DepositAccount.objects.get_or_create(
        user=user,
        defaults={
            'account_number': f'DEP-{user.id}',
            'balance': Decimal('1000.00'),
        }
    )
    print(f"✅ 예치금 계좌: ${deposit_account.balance}")
    
    # 7. 종목 확인 (NVDA)
    try:
        stock = Stock.objects.get(stock_code='NVDA')
        print(f"✅ 종목: {stock.stock_code} - {stock.stock_name}")
        
        # 8. 주가 데이터 확인
        latest_price = StockPrice.objects.filter(stock=stock).order_by('-date').first()
        if not latest_price:
            print("⚠️ 주가 데이터가 없습니다. StockPrice를 먼저 추가하세요.")
            print("   (시뮬레이션 모드는 StockPrice 테이블 사용)")
            return
        
        print(f"✅ 최신 주가: ${latest_price.close_price}")
        
        # 9. 투자 실행
        if savings > 0:
            print(f"\n💼 투자 실행: ${savings}으로 {stock.stock_code} 매수")
            
            # SavingsReward 생성
            reward = SavingsReward.objects.create(
                account=account,
                savings_amount=savings,
                period_start=timezone.now().replace(day=1).date(),
                period_end=timezone.now().date(),
                budget=account.monthly_budget or Decimal('0'),
                actual_spent=account.current_month_spent,
                stock=stock,
                purchase_price=Decimal('0'),
                purchase_date=timezone.now(),
                shares=Decimal('0'),
                status='pending'
            )
            
            # 투자 서비스 실행
            trading_service = TradingService(deposit_account=deposit_account)
            reward = trading_service.execute_investment(reward)
            
            print(f"✅ 투자 완료:")
            print(f"   - 매수 가격: ${reward.purchase_price}")
            print(f"   - 매수 주수: {reward.shares}")
            print(f"   - 상태: {reward.status}")
            
            # 10. 주가 업데이트 (상승 시나리오)
            print(f"\n📈 주가 상승 시나리오 테스트")
            reward.current_price = reward.purchase_price * Decimal('1.2')  # 20% 상승
            reward.update_current_value()
            
            print(f"   - 현재가: ${reward.current_price}")
            print(f"   - 현재 가치: ${reward.current_value}")
            print(f"   - 수익률: {reward.return_rate}%")
            print(f"   - 수익 상태: {'✅' if reward.is_profitable else '❌'}")
            print(f"   - 매도 가능: {'✅' if reward.can_sell else '❌'}")
            
            # 11. 매도 테스트 (수익일 때)
            if reward.can_sell:
                print(f"\n💰 매도 실행")
                reward, net_proceeds = trading_service.execute_sale(reward)
                print(f"   - 순수익: ${net_proceeds}")
                print(f"   - 상태: {reward.status}")
                print(f"   - 계좌 잔액: ${account.balance}")
            
            # 12. 손실 시나리오 테스트
            print(f"\n📉 손실 시나리오 테스트")
            reward2 = SavingsReward.objects.create(
                account=account,
                savings_amount=Decimal('50.00'),
                period_start=timezone.now().replace(day=1).date(),
                period_end=timezone.now().date(),
                budget=account.monthly_budget or Decimal('0'),
                actual_spent=Decimal('50.00'),
                stock=stock,
                purchase_price=Decimal('500.00'),
                purchase_date=timezone.now(),
                shares=Decimal('0.1'),
                status='invested'
            )
            
            reward2.current_price = Decimal('450.00')  # 10% 하락
            reward2.update_current_value()
            
            print(f"   - 현재가: ${reward2.current_price}")
            print(f"   - 수익률: {reward2.return_rate}%")
            print(f"   - 매도 가능: {'✅' if reward2.can_sell else '❌ (보유 강제)'}")
            
            if not reward2.can_sell:
                print(f"   ✅ 손실 상태에서는 매도 불가 (보유 강제)")
        
    except Stock.DoesNotExist:
        print("❌ NVDA 종목이 없습니다.")
    except Exception as e:
        print(f"❌ 에러: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)

if __name__ == '__main__':
    test_full_flow()

