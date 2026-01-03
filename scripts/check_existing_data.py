"""
기존 DB 데이터 상태 확인
"""

import os
import sys
import django

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock, StockFinancialRaw


def check_stock_data(ticker):
    """종목 데이터 상세 확인"""
    try:
        stock = Stock.objects.get(stock_code=ticker)
    except:
        print(f"X {ticker} - 종목 없음")
        return
    
    financials = StockFinancialRaw.objects.filter(stock=stock).order_by(
        '-disclosure_year', '-disclosure_quarter'
    )
    
    print(f"\n{ticker} - {stock.stock_name}")
    print(f"  총 분기: {financials.count()}개")
    print(f"  데이터 소스:")
    
    # 데이터 소스별 통계
    sources = financials.values_list('data_source', flat=True).distinct()
    for source in sources:
        count = financials.filter(data_source=source).count()
        print(f"    - {source}: {count}개")
    
    # 최근 5개 분기
    print(f"\n  최근 5개 분기:")
    for f in financials[:5]:
        ocf = "O" if f.ocf else "X"
        ni = "O" if f.net_income else "X"
        rev = "O" if f.revenue else "X"
        capex = "O" if f.capex else "X"
        
        print(f"    {f.disclosure_year}Q{f.disclosure_quarter} ({f.disclosure_date})")
        print(f"      OCF:{ocf} NI:{ni} Rev:{rev} CAPEX:{capex} [{f.data_source}]")


def main():
    """메인"""
    
    TEST_STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'META', 'TSLA']
    
    print("="*60)
    print(" 기존 DB 데이터 확인")
    print("="*60)
    
    for ticker in TEST_STOCKS:
        check_stock_data(ticker)
    
    print("\n" + "="*60)


if __name__ == '__main__':
    main()

