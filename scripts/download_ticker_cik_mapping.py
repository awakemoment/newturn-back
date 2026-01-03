"""
SEC ticker → CIK 매핑 데이터 다운로드 및 DB 업데이트
"""
import os
import sys
import django
import requests
import json

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock

HEADERS = {
    'User-Agent': 'NewTurn Investment Platform admin@newturn.com',
}

def download_ticker_cik_mapping():
    """SEC에서 ticker → CIK 매핑 다운로드"""
    print("📥 SEC ticker-CIK 매핑 다운로드 중...")
    
    url = "https://www.sec.gov/files/company_tickers.json"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ {len(data)}개 매핑 다운로드 완료")
        return data
    except Exception as e:
        print(f"❌ 다운로드 실패: {e}")
        return None


def update_stock_cik(mapping_data):
    """Stock 테이블에 CIK 업데이트"""
    print("\n📝 Stock 테이블 업데이트 중...")
    
    # CIK 필드가 없다면 추가 필요
    # (모델에 cik_number 필드 추가 필요)
    
    updated_count = 0
    not_found_count = 0
    
    # 매핑 데이터를 ticker → CIK 딕셔너리로 변환
    ticker_to_cik = {}
    for key, item in mapping_data.items():
        ticker = item['ticker']
        cik = str(item['cik_str']).zfill(10)  # 10자리로 패딩
        ticker_to_cik[ticker.upper()] = cik
    
    # DB의 모든 US 종목 업데이트
    stocks = Stock.objects.filter(country='us')
    
    for stock in stocks:
        ticker = stock.stock_code.upper()
        
        if ticker in ticker_to_cik:
            cik = ticker_to_cik[ticker]
            
            # corp_code 필드에 CIK 저장 (기존 필드 활용)
            stock.corp_code = cik
            stock.save(update_fields=['corp_code'])
            
            updated_count += 1
        else:
            not_found_count += 1
    
    print(f"✅ {updated_count:,}개 종목 CIK 업데이트 완료")
    print(f"⚠️ {not_found_count:,}개 종목 CIK 없음 (상장폐지/신규상장)")
    
    return updated_count


def main():
    print("\n" + "="*70)
    print("🔄 SEC Ticker-CIK 매핑 업데이트")
    print("="*70 + "\n")
    
    # 1. 매핑 데이터 다운로드
    mapping_data = download_ticker_cik_mapping()
    
    if not mapping_data:
        print("\n❌ 실패!")
        return
    
    # 2. Stock 테이블 업데이트
    updated = update_stock_cik(mapping_data)
    
    # 3. 샘플 확인
    print("\n📊 샘플 확인:")
    print("-" * 70)
    
    sample_stocks = Stock.objects.filter(
        country='us',
        corp_code__isnull=False
    ).exclude(corp_code='')[:5]
    
    for stock in sample_stocks:
        print(f"  {stock.stock_code:6s} → CIK: {stock.corp_code}")
    
    print("\n" + "="*70)
    print("✅ 완료!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()

