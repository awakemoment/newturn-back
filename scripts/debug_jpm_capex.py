"""
JPM의 CAPEX 필드 디버그 스크립트
- JPM의 모든 CAPEX 관련 필드 찾기
- 실제 데이터 확인
"""

import os
import sys
import django
import requests
from sec_cik_mapper import StockMapper
from datetime import datetime
import json

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


def debug_jpm_capex():
    """JPM의 CAPEX 필드 찾기"""
    
    print(f"\n{'='*70}")
    print(f" JPM CAPEX 필드 탐색")
    print(f"{'='*70}")
    
    # EDGAR 데이터 가져오기
    full_data, facts, error = get_edgar_data('JPM')
    
    if error:
        print(f"  X EDGAR 오류: {error}")
        return
    
    print(f"  OK EDGAR 데이터 획득")
    print(f"  총 필드 수: {len(facts)}")
    
    # CAPEX 관련 키워드로 필드 찾기 (더 광범위하게)
    capex_keywords = [
        'Payment', 'Payments', 'Capital', 'Property', 'Plant', 'Equipment',
        'Acquire', 'Purchase', 'Investment', 'Expenditure', 'Expenditures',
        'PPE', 'Intangible', 'Asset', 'Assets'
    ]
    
    print(f"\n  CAPEX 관련 필드 (광범위 검색):")
    capex_candidates = []
    
    for field_name in facts.keys():
        # 키워드 매칭
        matches = [kw for kw in capex_keywords if kw.lower() in field_name.lower()]
        if matches:
            units = facts[field_name].get('units', {}).get('USD', [])
            count_10q = sum(1 for item in units if item.get('form') == '10-Q')
            count_10k = sum(1 for item in units if item.get('form') == '10-K')
            
            if count_10q + count_10k > 0:
                capex_candidates.append({
                    'field': field_name,
                    'count_10q': count_10q,
                    'count_10k': count_10k,
                    'total': count_10q + count_10k,
                    'matches': matches
                })
    
    # 분기별 데이터 수로 정렬
    capex_candidates.sort(key=lambda x: x['total'], reverse=True)
    
    for candidate in capex_candidates[:20]:  # 상위 20개만 출력
        print(f"\n    - {candidate['field']}")
        print(f"      10-Q: {candidate['count_10q']}개, 10-K: {candidate['count_10k']}개")
        print(f"      매칭 키워드: {', '.join(candidate['matches'])}")
        
        # 실제 데이터 샘플 보기 (최근 5개)
        units = facts[candidate['field']].get('units', {}).get('USD', [])
        quarterly_items = [item for item in units if item.get('form') in ['10-Q', '10-K']]
        quarterly_items.sort(key=lambda x: x.get('end', ''), reverse=True)
        
        print(f"      최근 데이터 샘플:")
        for item in quarterly_items[:5]:
            fiscal_date = item.get('end', 'N/A')
            value = item.get('val', 0)
            form = item.get('form', 'N/A')
            print(f"        {fiscal_date} ({form}): {value:,.0f}")
    
    # Cash Flow Statement에서 CAPEX 찾기
    print(f"\n  Cash Flow Statement 관련 필드:")
    cf_keywords = ['Cash', 'Flow', 'Operating', 'Investing', 'Financing']
    cf_candidates = []
    
    for field_name in facts.keys():
        matches = [kw for kw in cf_keywords if kw.lower() in field_name.lower()]
        if 'Payment' in field_name or 'Purchase' in field_name or 'Investment' in field_name:
            if matches:
                units = facts[field_name].get('units', {}).get('USD', [])
                count_10q = sum(1 for item in units if item.get('form') == '10-Q')
                count_10k = sum(1 for item in units if item.get('form') == '10-K')
                
                if count_10q + count_10k > 0:
                    cf_candidates.append({
                        'field': field_name,
                        'count_10q': count_10q,
                        'count_10k': count_10k,
                        'total': count_10q + count_10k
                    })
    
    cf_candidates.sort(key=lambda x: x['total'], reverse=True)
    
    for candidate in cf_candidates[:10]:  # 상위 10개만 출력
        print(f"\n    - {candidate['field']}")
        print(f"      10-Q: {candidate['count_10q']}개, 10-K: {candidate['count_10k']}개")


if __name__ == '__main__':
    debug_jpm_capex()

