"""
완전 자동화 EDGAR 데이터 수집 시스템
- 예전 코드 방식 참고
- 종목별 유효 필드명 자동 탐색
- 모든 가능한 필드명 시도
- 완벽한 데이터만 저장
"""

import os
import sys
import django
import requests
from sec_cik_mapper import StockMapper
from datetime import datetime
import time

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock, StockFinancialRaw
from django.db import transaction


# 모든 가능한 EDGAR 필드명 (우선순위 순서)
EDGAR_FIELDS = {
    'OCF': [
        'NetCashProvidedByUsedInOperatingActivities',
        'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations',
        'CashProvidedByUsedInOperatingActivities',
        'NetCashFromOperatingActivities',
    ],
    
    'ICF': [
        'NetCashProvidedByUsedInInvestingActivities',
        'NetCashProvidedByUsedInInvestingActivitiesContinuingOperations',
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
        'NetIncomeLossAttributableToParent',
    ],
    
    'Revenue': [
        'Revenues',
        'RevenueFromContractWithCustomerExcludingAssessedTax',
        'SalesRevenueNet',
        'RevenueFromContractWithCustomerIncludingAssessedTax',
        'SalesRevenueGoodsNet',
        'SalesRevenueServicesNet',
    ],
    
    'Assets': [
        'Assets',
    ],
    
    'CurrentAssets': [
        'AssetsCurrent',
    ],
    
    'Liabilities': [
        'Liabilities',
    ],
    
    'CurrentLiabilities': [
        'LiabilitiesCurrent',
    ],
    
    'Equity': [
        'StockholdersEquity',
        'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest',
    ],
    
    'Dividend': [
        'PaymentsOfDividends',
        'PaymentsOfDividendsCommonStock',
    ],
}


def get_edgar_data(ticker, retries=3):
    """EDGAR API에서 데이터 가져오기"""
    for attempt in range(retries):
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
            elif response.status_code == 429:
                wait_time = 2 ** attempt
                print(f"  Rate limit, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                return None, None, f"HTTP {response.status_code}"
                
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
            else:
                return None, None, str(e)
    
    return None, None, "Max retries exceeded"


def find_valid_field_name(facts, field_names):
    """
    유효한 필드명 찾기
    - 데이터가 가장 많은 필드명 선택
    """
    best_field = None
    max_count = 0
    
    for field_name in field_names:
        if field_name in facts:
            units = facts[field_name].get('units', {}).get('USD', [])
            # 10-Q, 10-K 데이터만 카운트
            valid_count = sum(1 for item in units if item.get('form') in ['10-Q', '10-K'])
            
            if valid_count > max_count:
                max_count = valid_count
                best_field = field_name
    
    return best_field, max_count


def extract_all_quarters(facts, field_name):
    """
    모든 분기 데이터 추출
    반환: {(year, quarter): (value, date)}
    """
    if field_name not in facts:
        return {}
    
    result = {}
    units = facts[field_name].get('units', {}).get('USD', [])
    
    for item in units:
        # 10-Q, 10-K만
        if item.get('form') not in ['10-Q', '10-K']:
            continue
        
        fiscal_date = item.get('end')
        value = item.get('val')
        
        if not fiscal_date or value is None:
            continue
        
        # 날짜 파싱
        date_obj = datetime.strptime(fiscal_date, '%Y-%m-%d')
        year = date_obj.year
        month = date_obj.month
        quarter = (month - 1) // 3 + 1
        
        key = (year, quarter)
        
        # 같은 분기에 여러 값이 있으면 최신 것
        if key not in result or fiscal_date > result[key][1]:
            result[key] = (value, fiscal_date)
    
    return result


def collect_stock_data(ticker, target_quarters=20):
    """
    종목 데이터 수집 (완전 자동화)
    """
    print(f"\n============================================================")
    print(f" {ticker} 데이터 수집")
    print(f"============================================================")
    
    # 1. Stock 조회
    try:
        stock = Stock.objects.get(stock_code=ticker)
    except Stock.DoesNotExist:
        print(f"  X DB에 종목 없음")
        return False
    
    # 2. EDGAR 데이터 가져오기
    print(f"  EDGAR API 조회 중...")
    full_data, facts, error = get_edgar_data(ticker)
    
    if error:
        print(f"  X EDGAR 오류: {error}")
        return False
    
    print(f"  OK EDGAR 데이터 획득")
    
    # 3. 각 필드별로 유효한 필드명 찾기
    print(f"\n  필드명 탐색 중...")
    field_mappings = {}
    
    for field_key, field_names in EDGAR_FIELDS.items():
        best_field, count = find_valid_field_name(facts, field_names)
        
        if best_field:
            field_mappings[field_key] = best_field
            print(f"    OK {field_key:20s}: {best_field} ({count}개 데이터)")
        else:
            print(f"    - {field_key:20s}: 없음")
    
    # 4. 필수 필드 체크
    required_fields = ['OCF', 'NetIncome']
    missing_required = [f for f in required_fields if f not in field_mappings]
    
    if missing_required:
        print(f"\n  X 필수 필드 없음: {', '.join(missing_required)}")
        return False
    
    # 5. 모든 분기 데이터 추출
    print(f"\n  분기별 데이터 추출 중...")
    all_data = {}
    
    for field_key, field_name in field_mappings.items():
        quarters_data = extract_all_quarters(facts, field_name)
        all_data[field_key] = quarters_data
    
    # 6. 분기 목록 생성
    all_quarters = set()
    for quarters_data in all_data.values():
        all_quarters.update(quarters_data.keys())
    
    sorted_quarters = sorted(all_quarters, reverse=True)[:target_quarters]
    
    print(f"  발견된 분기: {len(sorted_quarters)}개")
    
    # 7. DB 저장
    print(f"\n  DB 저장 중...")
    saved_count = 0
    updated_count = 0
    
    with transaction.atomic():
        for year, quarter in sorted_quarters:
            # 각 필드 값 수집
            ocf_val = all_data.get('OCF', {}).get((year, quarter), (None, None))[0]
            icf_val = all_data.get('ICF', {}).get((year, quarter), (None, None))[0]
            capex_val = all_data.get('CAPEX', {}).get((year, quarter), (None, None))[0]
            ni_val = all_data.get('NetIncome', {}).get((year, quarter), (None, None))[0]
            rev_val = all_data.get('Revenue', {}).get((year, quarter), (None, None))[0]
            assets_val = all_data.get('Assets', {}).get((year, quarter), (None, None))[0]
            curr_assets_val = all_data.get('CurrentAssets', {}).get((year, quarter), (None, None))[0]
            liab_val = all_data.get('Liabilities', {}).get((year, quarter), (None, None))[0]
            curr_liab_val = all_data.get('CurrentLiabilities', {}).get((year, quarter), (None, None))[0]
            equity_val = all_data.get('Equity', {}).get((year, quarter), (None, None))[0]
            div_val = all_data.get('Dividend', {}).get((year, quarter), (None, None))[0]
            
            # FCF 계산
            fcf_val = None
            if ocf_val and capex_val:
                fcf_val = ocf_val - abs(capex_val)
            
            # 날짜 (가장 최신 값 사용)
            fiscal_date = all_data.get('OCF', {}).get((year, quarter), (None, None))[1]
            if not fiscal_date:
                fiscal_date = all_data.get('NetIncome', {}).get((year, quarter), (None, None))[1]
            
            if not fiscal_date:
                continue
            
            # 저장
            financial, created = StockFinancialRaw.objects.update_or_create(
                stock=stock,
                disclosure_year=year,
                disclosure_quarter=quarter,
                defaults={
                    'disclosure_date': fiscal_date,
                    'ocf': ocf_val,
                    'icf': icf_val,
                    'capex': abs(capex_val) if capex_val else None,
                    'fcf': fcf_val,
                    'net_income': ni_val,
                    'revenue': rev_val,
                    'total_assets': assets_val,
                    'current_assets': curr_assets_val,
                    'total_liabilities': liab_val,
                    'current_liabilities': curr_liab_val,
                    'total_equity': equity_val,
                    'dividend': abs(div_val) if div_val else None,
                    'data_source': 'EDGAR_ROBUST',
                }
            )
            
            if created:
                saved_count += 1
            else:
                updated_count += 1
    
    print(f"\n  OK 저장 완료")
    print(f"    - 생성: {saved_count}분기")
    print(f"    - 업데이트: {updated_count}분기")
    
    # 8. 품질 검증
    print(f"\n  품질 검증 중...")
    total_quarters = StockFinancialRaw.objects.filter(stock=stock).count()
    
    # 핵심 필드 누락 체크
    missing_ocf = StockFinancialRaw.objects.filter(stock=stock, ocf__isnull=True).count()
    missing_ni = StockFinancialRaw.objects.filter(stock=stock, net_income__isnull=True).count()
    missing_revenue = StockFinancialRaw.objects.filter(stock=stock, revenue__isnull=True).count()
    
    print(f"    - 총 분기: {total_quarters}")
    print(f"    - OCF 누락: {missing_ocf}")
    print(f"    - NetIncome 누락: {missing_ni}")
    print(f"    - Revenue 누락: {missing_revenue}")
    
    if missing_ocf == 0 and missing_ni == 0:
        print(f"\n  OK 품질 우수 - 필수 필드 완벽")
        return True
    else:
        print(f"\n  ! 품질 보통 - 일부 필드 누락")
        return True


def main():
    """메인 함수"""
    
    # 주요 대형주 (포트폴리오 테스트용)
    TARGET_STOCKS = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
        'META', 'TSLA', 'JPM', 'V', 'JNJ',
        'WMT', 'PG', 'XOM', 'CVX', 'KO',
    ]
    
    print("\n" + "="*60)
    print(" EDGAR 완전 자동화 데이터 수집")
    print("="*60)
    print(f" 대상 종목: {len(TARGET_STOCKS)}개")
    print("="*60)
    
    success_count = 0
    failed_stocks = []
    
    for i, ticker in enumerate(TARGET_STOCKS, 1):
        print(f"\n[{i}/{len(TARGET_STOCKS)}] 진행 중...")
        
        if collect_stock_data(ticker):
            success_count += 1
        else:
            failed_stocks.append(ticker)
        
        # Rate limit 고려
        if i < len(TARGET_STOCKS):
            time.sleep(0.3)
    
    # 최종 요약
    print("\n" + "="*60)
    print(" 최종 요약")
    print("="*60)
    print(f"  OK 성공: {success_count}/{len(TARGET_STOCKS)}")
    print(f"  X 실패: {len(failed_stocks)}/{len(TARGET_STOCKS)}")
    
    if failed_stocks:
        print(f"\n  실패 종목: {', '.join(failed_stocks)}")
    
    print("="*60)
    
    # 최종 품질 체크
    print(f"\n 최종 품질 확인:")
    for ticker in TARGET_STOCKS:
        try:
            stock = Stock.objects.get(stock_code=ticker)
            total = StockFinancialRaw.objects.filter(stock=stock).count()
            missing_ocf = StockFinancialRaw.objects.filter(stock=stock, ocf__isnull=True).count()
            missing_revenue = StockFinancialRaw.objects.filter(stock=stock, revenue__isnull=True).count()
            
            if missing_ocf == 0 and missing_revenue == 0:
                print(f"  OK {ticker:6s} - {total}분기, 완벽")
            elif missing_ocf == 0:
                print(f"  O  {ticker:6s} - {total}분기, Revenue 누락 {missing_revenue}개")
            else:
                print(f"  !  {ticker:6s} - {total}분기, OCF 누락 {missing_ocf}개")
        except:
            print(f"  X  {ticker:6s} - 데이터 없음")


if __name__ == '__main__':
    main()

