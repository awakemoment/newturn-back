"""
관심종목 API 테스트
"""
import os
import sys
import django

# Django 설정
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock
from apps.watchlist.models import Watchlist
from django.contrib.auth import get_user_model

User = get_user_model()

def test_watchlist():
    print("=" * 80)
    print("📋 관심종목 API 테스트")
    print("=" * 80)
    
    # 1. dev_user 생성/조회
    print("\n1️⃣ dev_user 확인...")
    user, created = User.objects.get_or_create(
        username='dev_user',
        defaults={
            'email': 'dev@newturn.com',
            'first_name': 'Dev',
            'last_name': 'User',
        }
    )
    print(f"   ✅ User: {user.email} (Created: {created})")
    
    # 2. 테스트 종목 조회
    print("\n2️⃣ 테스트 종목 조회...")
    test_stock = Stock.objects.filter(stock_code='AAPL').first()
    if not test_stock:
        print("   ❌ AAPL 종목을 찾을 수 없습니다!")
        # 아무 종목이나 선택
        test_stock = Stock.objects.first()
        if not test_stock:
            print("   ❌ 종목이 하나도 없습니다!")
            return
    
    print(f"   ✅ Stock: {test_stock.stock_name} ({test_stock.stock_code})")
    
    # 3. 기존 관심종목 삭제
    print("\n3️⃣ 기존 관심종목 삭제...")
    deleted_count, _ = Watchlist.objects.filter(user=user, stock=test_stock).delete()
    print(f"   ✅ 삭제: {deleted_count}개")
    
    # 4. 관심종목 추가
    print("\n4️⃣ 관심종목 추가...")
    try:
        watchlist = Watchlist.objects.create(
            user=user,
            stock=test_stock,
            memo="테스트 메모",
            preferred_mate="benjamin",
        )
        print(f"   ✅ 추가 성공: ID={watchlist.id}")
        print(f"      - Stock: {watchlist.stock.stock_name}")
        print(f"      - User: {watchlist.user.email}")
        print(f"      - Memo: {watchlist.memo}")
        print(f"      - Preferred Mate: {watchlist.preferred_mate}")
    except Exception as e:
        print(f"   ❌ 추가 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 5. 관심종목 조회
    print("\n5️⃣ 관심종목 조회...")
    watchlists = Watchlist.objects.filter(user=user)
    print(f"   ✅ 총 {watchlists.count()}개")
    for wl in watchlists[:5]:
        print(f"      - {wl.stock.stock_name} ({wl.stock.stock_code})")
    
    # 6. 적정가격 계산 테스트
    print("\n6️⃣ 적정가격 계산 테스트...")
    from apps.stocks.models import StockFinancialRaw, StockPrice
    from apps.analysis.models import ProperPrice
    
    recent_4q = list(StockFinancialRaw.objects.filter(
        stock=test_stock,
        data_source='EDGAR'
    ).order_by('-disclosure_year', '-disclosure_quarter')[:4])
    
    if len(recent_4q) < 4:
        print(f"   ⚠️ 재무 데이터 부족: {len(recent_4q)}개 (최소 4개 필요)")
    else:
        print(f"   ✅ 재무 데이터: {len(recent_4q)}개")
        
        # TTM 계산
        ttm_fcf = sum([q.fcf or 0 for q in recent_4q])
        ttm_net_income = sum([q.net_income or 0 for q in recent_4q])
        ttm_revenue = sum([q.revenue or 0 for q in recent_4q])
        
        print(f"      - TTM FCF: ${ttm_fcf:,.0f}")
        print(f"      - TTM Net Income: ${ttm_net_income:,.0f}")
        print(f"      - TTM Revenue: ${ttm_revenue:,.0f}")
    
    # 7. 주가 확인
    print("\n7️⃣ 주가 데이터 확인...")
    latest_price = StockPrice.objects.filter(stock=test_stock).order_by('-date').first()
    if latest_price:
        print(f"   ✅ 최신 주가: ${latest_price.close_price} ({latest_price.date})")
    else:
        print(f"   ⚠️ 주가 데이터 없음 (collect_stock_prices.py 실행 필요)")
    
    # 8. 적정가격 확인
    print("\n8️⃣ 적정가격 확인...")
    proper_prices = ProperPrice.objects.filter(stock=test_stock)
    if proper_prices.exists():
        print(f"   ✅ 적정가격: {proper_prices.count()}개")
        for pp in proper_prices:
            print(f"      - {pp.mate_type}: ${pp.proper_price} (괴리율: {pp.gap_ratio}%)")
    else:
        print(f"   ⚠️ 적정가격 없음 (관심종목 추가 시 자동 계산됨)")
    
    print("\n" + "=" * 80)
    print("✅ 테스트 완료!")
    print("=" * 80)

if __name__ == '__main__':
    test_watchlist()

