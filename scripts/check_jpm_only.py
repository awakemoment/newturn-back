"""
JPM 데이터 품질 확인 스크립트
"""

import os
import sys
import django

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock, StockFinancialRaw


def check_jpm():
    """JPM 데이터 확인"""
    
    print("\n" + "="*60)
    print(" JPM 데이터 확인")
    print("="*60)
    
    try:
        stock = Stock.objects.get(stock_code='JPM')
        print(f"\nOK 종목: {stock.stock_name}")
        
        # 전체 데이터 확인
        financials = StockFinancialRaw.objects.filter(stock=stock).order_by(
            'disclosure_year', 'disclosure_quarter'
        )
        
        total = financials.count()
        print(f"  총 분기: {total}개")
        
        # 필드별 누락 확인
        missing_ocf = financials.filter(ocf__isnull=True).count()
        missing_net_income = financials.filter(net_income__isnull=True).count()
        missing_revenue = financials.filter(revenue__isnull=True).count()
        missing_capex = financials.filter(capex__isnull=True).count()
        
        print(f"\n  필드별 누락:")
        print(f"    OCF:        {missing_ocf}/{total}")
        print(f"    NetIncome:  {missing_net_income}/{total}")
        print(f"    Revenue:    {missing_revenue}/{total}")
        print(f"    CAPEX:      {missing_capex}/{total}")
        
        # 최근 5개 분기 상세 확인
        print(f"\n  최근 5개 분기 상세:")
        recent = financials.order_by('-disclosure_year', '-disclosure_quarter')[:5]
        
        for f in recent:
            capex_str = f"{f.capex:,.0f}" if f.capex else "없음"
            revenue_str = f"{f.revenue:,.0f}" if f.revenue else "없음"
            print(f"    {f.disclosure_year}Q{f.disclosure_quarter}: CAPEX={capex_str}, Revenue={revenue_str}")
        
        # 상태 판단
        if missing_capex == 0:
            print("\n  ✓ CAPEX 완벽!")
        elif missing_capex < total:
            print(f"\n  ⚠ CAPEX 일부 누락 ({missing_capex}/{total})")
        else:
            print(f"\n  ✗ CAPEX 전체 누락")
            
    except Stock.DoesNotExist:
        print("\n  ✗ JPM 종목을 찾을 수 없습니다")
    except Exception as e:
        print(f"\n  ✗ 오류: {e}")


if __name__ == '__main__':
    check_jpm()

