"""
데이터 초기화 및 재수집
- 잘못된 데이터 삭제
- 원래 스크립트로 재수집
"""

import os
import sys
import django

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock, StockFinancialRaw


def reset_stock_data(ticker):
    """종목 데이터 초기화"""
    try:
        stock = Stock.objects.get(stock_code=ticker)
        
        # 모든 재무 데이터 삭제
        deleted_count = StockFinancialRaw.objects.filter(stock=stock).delete()[0]
        
        print(f"  {ticker}: {deleted_count}개 삭제")
        return True
        
    except Stock.DoesNotExist:
        print(f"  {ticker}: 종목 없음")
        return False


def main():
    """메인"""
    
    # 주요 종목들만
    TARGET_STOCKS = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
        'META', 'TSLA', 'JPM', 'V', 'JNJ',
        'WMT', 'PG', 'XOM', 'CVX', 'KO',
    ]
    
    print("\n" + "="*60)
    print(" 데이터 초기화")
    print("="*60)
    
    for ticker in TARGET_STOCKS:
        reset_stock_data(ticker)
    
    print("\n" + "="*60)
    print(" 초기화 완료!")
    print(" 이제 collect_financial_data.py를 실행하세요:")
    print(" python scripts/collect_financial_data.py --limit 15")
    print("="*60)


if __name__ == '__main__':
    main()

