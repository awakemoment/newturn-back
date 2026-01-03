"""
주요 대형주 데이터 확인
"""

import os
import sys
import django

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock, StockFinancialRaw

# 주요 대형주만
MAJOR_STOCKS = [
    'AAPL',   # Apple
    'MSFT',   # Microsoft
    'GOOGL',  # Google
    'AMZN',   # Amazon
    'NVDA',   # NVIDIA
    'META',   # Meta
    'TSLA',   # Tesla
    'BRK.B',  # Berkshire Hathaway
    'JPM',    # JPMorgan
    'V',      # Visa
]

print("\n" + "="*60)
print("📊 주요 대형주 DB 확인")
print("="*60)

for ticker in MAJOR_STOCKS:
    try:
        stock = Stock.objects.get(stock_code=ticker)
        financials_count = StockFinancialRaw.objects.filter(stock=stock).count()
        
        if financials_count > 0:
            latest = StockFinancialRaw.objects.filter(stock=stock).order_by('-disclosure_date').first()
            print(f"✅ {ticker:6s} - {stock.stock_name:30s} | 재무 데이터: {financials_count}분기 | 최신: {latest.disclosure_date}")
        else:
            print(f"⚠️ {ticker:6s} - {stock.stock_name:30s} | 재무 데이터 없음")
            
    except Stock.DoesNotExist:
        print(f"❌ {ticker:6s} - DB에 종목 없음")

print("="*60)

