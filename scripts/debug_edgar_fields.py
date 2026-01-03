"""
EDGAR 필드명 디버그 스크립트
- 특정 종목의 모든 가능한 필드 확인
- Revenue, CAPEX 관련 필드 탐색
"""

import os
import sys
import django
import requests
from sec_cik_mapper import StockMapper

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()


def get_edgar_data(ticker):
    """EDGAR API에서 데이터 가져오기"""
    try:
        mapper = StockMapper()
        cik = mapper.ticker_to_cik.get(ticker)
        
        if not cik:
            return None, None, "CIK not found"
        
        cik_str = str(cik).zfill(10)
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_str}.json"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            facts = data.get('facts', {}).get('us-gaap', {})
            return data, facts, None
        else:
            return None, None, f"HTTP {response.status_code}"
            
    except Exception as e:
        return None, None, str(e)


def debug_fields(ticker):
    """특정 종목의 모든 필드 탐색"""
    
    print(f"\n{'='*60}")
    print(f" {ticker} 필드 탐색")
    print(f"{'='*60}")
    
    # EDGAR 데이터 가져오기
    full_data, facts, error = get_edgar_data(ticker)
    
    if error:
        print(f"  X EDGAR 오류: {error}")
        return
    
    print(f"  OK EDGAR 데이터 획득")
    print(f"  총 필드 수: {len(facts)}")
    
    # Revenue 관련 필드 찾기
    print(f"\n  Revenue 관련 필드:")
    revenue_fields = [f for f in facts.keys() if 'Revenue' in f or 'Sales' in f or 'Income' in f]
    
    for field in sorted(revenue_fields):
        units = facts[field].get('units', {}).get('USD', [])
        count_10q = sum(1 for item in units if item.get('form') == '10-Q')
        count_10k = sum(1 for item in units if item.get('form') == '10-K')
        
        if count_10q + count_10k > 0:
            print(f"    - {field}")
            print(f"      10-Q: {count_10q}개, 10-K: {count_10k}개")
    
    # CAPEX 관련 필드 찾기
    print(f"\n  CAPEX 관련 필드:")
    capex_fields = [f for f in facts.keys() if 'Payment' in f and ('Property' in f or 'Capital' in f or 'Acquire' in f)]
    
    for field in sorted(capex_fields):
        units = facts[field].get('units', {}).get('USD', [])
        count_10q = sum(1 for item in units if item.get('form') == '10-Q')
        count_10k = sum(1 for item in units if item.get('form') == '10-K')
        
        if count_10q + count_10k > 0:
            print(f"    - {field}")
            print(f"      10-Q: {count_10q}개, 10-K: {count_10k}개")


def main():
    """문제 종목들 디버그"""
    
    # Revenue 누락이 심한 종목들
    PROBLEM_STOCKS = [
        'AAPL',   # Revenue 20개 누락
        'MSFT',   # Revenue 20개 누락
        'JNJ',    # Revenue 20개 누락
        'V',      # Revenue 19개 누락
    ]
    
    print("\n" + "="*60)
    print(" EDGAR 필드 디버그")
    print("="*60)
    
    for ticker in PROBLEM_STOCKS:
        debug_fields(ticker)
    
    print("\n" + "="*60)
    print(" 디버그 완료")
    print("="*60)


if __name__ == '__main__':
    main()

