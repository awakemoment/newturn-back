"""
EDGAR 데이터 누락 보완 스크립트
- 대체 필드명으로 재시도
- 계산으로 유도 가능한 지표는 계산
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

from apps.stocks.models import Stock, StockFinancialRaw


# EDGAR 필드명 매핑 (여러 가능한 이름들)
FIELD_MAPPINGS = {
    'OCF': [
        'NetCashProvidedByUsedInOperatingActivities',
        'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations',
        'CashProvidedByUsedInOperatingActivities',
    ],
    'CAPEX': [
        'PaymentsToAcquirePropertyPlantAndEquipment',
        'PaymentsForCapitalImprovements',
        'PaymentsToAcquireProductiveAssets',
    ],
    'NetIncome': [
        'NetIncomeLoss',
        'ProfitLoss',
        'NetIncomeLossAvailableToCommonStockholdersBasic',
    ],
    'Revenue': [
        'Revenues',
        'RevenueFromContractWithCustomerExcludingAssessedTax',
        'SalesRevenueNet',
        'RevenueFromContractWithCustomerIncludingAssessedTax',
    ],
    'Assets': [
        'Assets',
        'AssetsCurrent',
    ],
    'Liabilities': [
        'Liabilities',
        'LiabilitiesCurrent',
    ],
    'Equity': [
        'StockholdersEquity',
        'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest',
    ],
}


def get_edgar_data(ticker):
    """EDGAR API에서 데이터 가져오기"""
    try:
        mapper = StockMapper()
        cik = mapper.ticker_to_cik.get(ticker)
        
        if not cik:
            return None, f"CIK not found"
        
        cik_str = str(cik).zfill(10)
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_str}.json"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"HTTP {response.status_code}"
            
    except Exception as e:
        return None, str(e)


def extract_value_with_fallback(facts, field_names):
    """
    여러 필드명으로 시도해서 값 추출
    """
    for field_name in field_names:
        if field_name in facts:
            units = facts[field_name].get('units', {}).get('USD', [])
            if units:
                # 가장 최신 값
                latest = sorted(units, key=lambda x: x.get('end', ''), reverse=True)[0]
                return latest.get('val')
    return None


def calculate_fcf(ocf, capex):
    """FCF 계산"""
    if ocf is not None and capex is not None:
        return ocf - abs(capex)  # CAPEX는 음수일 수 있음
    return None


def fix_missing_data(ticker, force_update=False):
    """
    특정 종목의 누락 데이터 보완
    """
    print(f"\n📊 {ticker} 데이터 보완 중...")
    
    # 1. Stock 조회
    try:
        stock = Stock.objects.get(stock_code=ticker)
    except Stock.DoesNotExist:
        print(f"  ❌ DB에 종목 없음")
        return False
    
    # 2. EDGAR 데이터 가져오기
    edgar_data, error = get_edgar_data(ticker)
    if error:
        print(f"  ❌ EDGAR 오류: {error}")
        return False
    
    facts = edgar_data.get('facts', {}).get('us-gaap', {})
    
    # 3. 모든 분기 데이터 추출
    ocf_data = extract_all_quarters(facts, FIELD_MAPPINGS['OCF'])
    capex_data = extract_all_quarters(facts, FIELD_MAPPINGS['CAPEX'])
    ni_data = extract_all_quarters(facts, FIELD_MAPPINGS['NetIncome'])
    rev_data = extract_all_quarters(facts, FIELD_MAPPINGS['Revenue'])
    
    # 4. DB 업데이트
    updated_count = 0
    
    for fiscal_date, ocf_val in ocf_data.items():
        capex_val = capex_data.get(fiscal_date)
        fcf_val = calculate_fcf(ocf_val, capex_val)
        ni_val = ni_data.get(fiscal_date)
        rev_val = rev_data.get(fiscal_date)
        
        # 연도와 분기 파싱
        year = int(fiscal_date[:4])
        month = int(fiscal_date[5:7])
        quarter = (month - 1) // 3 + 1
        
        # 업데이트 또는 생성
        financial, created = StockFinancialRaw.objects.update_or_create(
            stock=stock,
            disclosure_year=year,
            disclosure_quarter=quarter,
            defaults={
                'disclosure_date': fiscal_date,
                'ocf': ocf_val,
                'capex': abs(capex_val) if capex_val else None,
                'fcf': fcf_val,
                'net_income': ni_val,
                'revenue': rev_val,
                'data_source': 'EDGAR',
            }
        )
        
        if created or force_update:
            updated_count += 1
    
    print(f"  ✅ {updated_count}개 분기 업데이트")
    return True


def extract_all_quarters(facts, field_names):
    """
    모든 분기 데이터 추출
    반환: {날짜: 값} 딕셔너리
    """
    result = {}
    
    for field_name in field_names:
        if field_name in facts:
            units = facts[field_name].get('units', {}).get('USD', [])
            for item in units:
                # 분기 데이터만 (form: "10-Q" or "10-K")
                if item.get('form') in ['10-Q', '10-K']:
                    fiscal_date = item.get('end')
                    value = item.get('val')
                    
                    if fiscal_date and value is not None:
                        # 이미 값이 있으면 덮어쓰지 않음 (첫 번째 필드명 우선)
                        if fiscal_date not in result:
                            result[fiscal_date] = value
    
    return result


def main():
    """주요 대형주 데이터 보완"""
    
    STOCKS_TO_FIX = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
        'META', 'TSLA', 'JPM', 'V',
    ]
    
    print("\n" + "="*60)
    print("🔧 EDGAR 데이터 보완 시작")
    print("="*60)
    
    success = 0
    failed = 0
    
    for ticker in STOCKS_TO_FIX:
        if fix_missing_data(ticker):
            success += 1
        else:
            failed += 1
    
    print("\n" + "="*60)
    print(f"✅ 성공: {success}개")
    print(f"❌ 실패: {failed}개")
    print("="*60)


if __name__ == '__main__':
    main()

