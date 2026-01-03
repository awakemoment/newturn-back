"""
미국 기업만 필터링 후 데이터 현황 확인
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock

def main():
    print("\n" + "="*70)
    print("🇺🇸 미국 기업 필터링 확인")
    print("="*70)
    
    # 전체 US 종목
    total_us = Stock.objects.filter(country='us').count()
    print(f"\n전체 US 종목: {total_us:,}개")
    
    # 외국 기업 필터
    foreign_keywords = ['PLC', 'SE', 'SA', 'NV', 'AB', 'ASA', 'Oyj', 'SpA', 'AG', 'Ltd.']
    
    us_only = Stock.objects.filter(country='us')
    
    # 외국 기업 제외
    for keyword in foreign_keywords:
        us_only = us_only.exclude(stock_name__icontains=keyword)
    
    us_only = us_only.exclude(stock_name__icontains='ADR')
    us_only = us_only.exclude(description__icontains='ADR')
    
    us_only_count = us_only.count()
    foreign_count = total_us - us_only_count
    
    print(f"\n🇺🇸 미국 기업만: {us_only_count:,}개")
    print(f"🌍 외국 기업: {foreign_count:,}개 (제외됨)")
    
    # 외국 기업 샘플
    print(f"\n🌍 제외된 외국 기업 샘플 (10개):")
    print("-" * 70)
    
    foreign_stocks = Stock.objects.filter(country='us').exclude(
        id__in=us_only.values_list('id', flat=True)
    )[:10]
    
    for stock in foreign_stocks:
        name = stock.stock_name[:40]
        print(f"  {stock.stock_code:6s} - {name:40s}")
    
    # EDGAR 데이터 현황
    print(f"\n💰 EDGAR 데이터 현황:")
    print("-" * 70)
    
    edgar_us_only = us_only.filter(
        financials_raw__data_source='EDGAR'
    ).distinct().count()
    
    missing_us_only = us_only_count - edgar_us_only
    
    print(f"  EDGAR 있음: {edgar_us_only:,}개")
    print(f"  EDGAR 없음: {missing_us_only:,}개 ← 수집 대상")
    
    print("\n" + "="*70)
    print("✅ 확인 완료!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()

