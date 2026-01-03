"""
관심종목 생성 시 적정가격 계산 테스트
"""
import os
import sys
import django

# Django 설정
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from decimal import Decimal
from apps.stocks.models import Stock, StockFinancialRaw, StockPrice
from apps.watchlist.models import Watchlist
from apps.analysis.models import ProperPrice
from django.contrib.auth import get_user_model
from core.utils.valuation_engine import calculate_all_mates_proper_price

User = get_user_model()

def test_proper_price_calculation():
    print("=" * 80)
    print("🧮 적정가격 계산 테스트")
    print("=" * 80)
    
    # 1. dev_user 및 종목 조회
    user, _ = User.objects.get_or_create(
        username='dev_user',
        defaults={'email': 'dev@newturn.com', 'first_name': 'Dev', 'last_name': 'User'}
    )
    
    stock = Stock.objects.filter(stock_code='AAPL').first()
    if not stock:
        stock = Stock.objects.first()
    
    print(f"\n📊 종목: {stock.stock_name} ({stock.stock_code})")
    
    # 2. 기존 적정가격 삭제
    ProperPrice.objects.filter(stock=stock).delete()
    print(f"✅ 기존 적정가격 삭제 완료")
    
    # 3. 재무 데이터 확인
    print(f"\n📈 재무 데이터 확인...")
    recent_4q = list(StockFinancialRaw.objects.filter(
        stock=stock,
        data_source='EDGAR'
    ).order_by('-disclosure_year', '-disclosure_quarter')[:4])
    
    if len(recent_4q) < 4:
        print(f"❌ 재무 데이터 부족: {len(recent_4q)}개 (최소 4개 필요)")
        return
    
    print(f"✅ 재무 데이터: {len(recent_4q)}개")
    
    ttm_fcf = sum([q.fcf or 0 for q in recent_4q])
    ttm_net_income = sum([q.net_income or 0 for q in recent_4q])
    ttm_revenue = sum([q.revenue or 0 for q in recent_4q])
    latest = recent_4q[0]
    
    print(f"   - TTM FCF: ${ttm_fcf:,.0f}")
    print(f"   - TTM Net Income: ${ttm_net_income:,.0f}")
    print(f"   - TTM Revenue: ${ttm_revenue:,.0f}")
    print(f"   - Total Equity: ${latest.total_equity:,.0f}")
    
    # 4. 성장률 계산
    previous_4q = list(StockFinancialRaw.objects.filter(
        stock=stock,
        data_source='EDGAR'
    ).order_by('-disclosure_year', '-disclosure_quarter')[4:8])
    
    revenue_growth = 0
    if len(previous_4q) == 4:
        prev_revenue = sum([q.revenue or 0 for q in previous_4q])
        if prev_revenue:
            revenue_growth = ((ttm_revenue - prev_revenue) / prev_revenue) * 100
    
    print(f"   - Revenue Growth: {revenue_growth:.2f}%")
    
    # 5. 현재가 확인
    print(f"\n💰 주가 데이터 확인...")
    latest_price = StockPrice.objects.filter(stock=stock).order_by('-date').first()
    if not latest_price:
        print(f"⚠️ 주가 데이터 없음! 기본값 $100 사용")
        current_price = 100.0
    else:
        current_price = float(latest_price.close_price)
        print(f"✅ 현재가: ${current_price} ({latest_price.date})")
    
    # 6. 적정가격 계산
    print(f"\n🎯 적정가격 계산 중...")
    
    indicators = {
        'ttm_fcf': ttm_fcf,
        'ttm_net_income': ttm_net_income,
        'total_equity': latest.total_equity,
        'revenue_growth': revenue_growth,
    }
    
    shares_outstanding = 1000000000  # 10억주 가정
    
    try:
        valuations = calculate_all_mates_proper_price(indicators, current_price, shares_outstanding)
        
        print(f"✅ 계산 성공!")
        print(f"\n📊 적정가격 결과:")
        print("-" * 80)
        
        for mate_type, valuation in valuations.items():
            mate_names = {
                'benjamin': '🎩 베니',
                'fisher': '🌱 그로우',
                'greenblatt': '🔮 매직',
                'lynch': '🎯 데일리'
            }
            
            print(f"\n{mate_names.get(mate_type, mate_type)}:")
            print(f"   적정가: ${valuation['proper_price']}")
            print(f"   현재가: ${current_price}")
            print(f"   괴리율: {valuation['gap_ratio']}%")
            print(f"   방법: {valuation['method']}")
            print(f"   추천: {valuation['recommendation']}")
            
            # DB 저장
            ProperPrice.objects.update_or_create(
                stock=stock,
                mate_type=mate_type,
                defaults={
                    'proper_price': valuation['proper_price'],
                    'current_price': Decimal(str(current_price)),
                    'gap_ratio': valuation['gap_ratio'],
                    'calculation_method': valuation['method'],
                }
            )
        
        print("\n" + "-" * 80)
        print(f"✅ DB 저장 완료!")
        
        # 7. 저장 확인
        saved_prices = ProperPrice.objects.filter(stock=stock)
        print(f"\n✅ 저장된 적정가격: {saved_prices.count()}개")
        
    except Exception as e:
        print(f"❌ 계산 실패: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("✅ 테스트 완료!")
    print("=" * 80)

if __name__ == '__main__':
    test_proper_price_calculation()

