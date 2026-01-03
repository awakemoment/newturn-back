"""
EDGAR 완전 자동화 데이터 수집 시스템 (통합 버전)
- 유효 필드명 자동 탐색
- 모든 가능한 필드명 시도
- 누락 데이터 자동 보완
- 품질 검증
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
        'RevenueFromContractWithCustomerIncludingAssessedTax',
        'SalesRevenueNet',
        'SalesRevenueGoodsNet',
        'SalesRevenueServicesNet',
        'RevenuesNetOfInterestExpense',  # 금융주
        'InterestAndDividendIncomeOperating',  # 금융주
        'FinancialServicesRevenue',  # 금융주
        'InterestIncomeOperating',  # 금융주
    ],
    
    'OperatingProfit': [
        'OperatingIncomeLoss',
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',
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


def find_valid_field_names(facts):
    """
    모든 필드에 대해 유효한 필드명 찾기
    반환: {field_key: (field_name, count)}
    """
    result = {}
    
    for field_key, field_names in EDGAR_FIELDS.items():
        best_field = None
        max_count = 0
        
        for field_name in field_names:
            if field_name not in facts:
                continue
            
            units = facts[field_name].get('units', {}).get('USD', [])
            # 10-Q, 10-K 데이터만 카운트
            valid_count = sum(1 for item in units if item.get('form') in ['10-Q', '10-K'])
            
            if valid_count > max_count:
                max_count = valid_count
                best_field = field_name
        
        if best_field:
            result[field_key] = (best_field, max_count)
    
    return result


def extract_all_quarters(facts, field_name):
    """
    모든 분기 데이터 추출 (유연한 매칭)
    반환: {(year, quarter): {'value': val, 'date': date, 'field': field_name}}
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
        
        # 분기 매칭 (유연하게)
        if month in [1, 2, 3]:
            quarter = 1
        elif month in [4, 5, 6]:
            quarter = 2
        elif month in [7, 8, 9]:
            quarter = 3
        else:  # 10, 11, 12
            quarter = 4
        
        key = (year, quarter)
        
        # 같은 분기에 여러 값이 있으면 최신 값
        if key not in result or fiscal_date > result[key]['date']:
            result[key] = {
                'value': value,
                'date': fiscal_date,
                'field': field_name
            }
    
    return result


def collect_stock_data(ticker, target_quarters=20, verbose=True):
    """
    종목 데이터 완전 수집 (자동 탐색 + 보완)
    """
    if verbose:
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
    if verbose:
        print(f"  EDGAR API 조회 중...")
    
    full_data, facts, error = get_edgar_data(ticker)
    
    if error:
        print(f"  X EDGAR 오류: {error}")
        return False
    
    if verbose:
        print(f"  OK EDGAR 데이터 획득")
    
    # 3. 유효한 필드명 찾기
    if verbose:
        print(f"\n  필드명 탐색 중...")
    
    field_mappings = find_valid_field_names(facts)
    
    if verbose:
        for field_key, (field_name, count) in field_mappings.items():
            print(f"    OK {field_key:20s}: {field_name} ({count}개)")
    
    # 4. 필수 필드 체크
    required_fields = ['OCF', 'NetIncome']
    missing_required = [f for f in required_fields if f not in field_mappings]
    
    if missing_required:
        print(f"  X 필수 필드 없음: {', '.join(missing_required)}")
        return False
    
    # 5. 모든 분기 데이터 추출
    if verbose:
        print(f"\n  분기별 데이터 추출 중...")
    
    all_data = {}
    for field_key, (field_name, _) in field_mappings.items():
        quarters_data = extract_all_quarters(facts, field_name)
        all_data[field_key] = quarters_data
    
    # 6. 분기 목록 생성 (모든 필드에서 발견된 분기)
    all_quarters = set()
    for quarters_data in all_data.values():
        all_quarters.update(quarters_data.keys())
    
    sorted_quarters = sorted(all_quarters, reverse=True)[:target_quarters]
    
    if verbose:
        print(f"  발견된 분기: {len(sorted_quarters)}개")
    
    # 7. DB 저장
    if verbose:
        print(f"\n  DB 저장 중...")
    
    saved_count = 0
    updated_count = 0
    
    with transaction.atomic():
        for year, quarter in sorted_quarters:
            # 각 필드 값 수집
            ocf_val = all_data.get('OCF', {}).get((year, quarter), {}).get('value')
            icf_val = all_data.get('ICF', {}).get((year, quarter), {}).get('value')
            capex_val = all_data.get('CAPEX', {}).get((year, quarter), {}).get('value')
            ni_val = all_data.get('NetIncome', {}).get((year, quarter), {}).get('value')
            rev_val = all_data.get('Revenue', {}).get((year, quarter), {}).get('value')
            op_val = all_data.get('OperatingProfit', {}).get((year, quarter), {}).get('value')
            assets_val = all_data.get('Assets', {}).get((year, quarter), {}).get('value')
            curr_assets_val = all_data.get('CurrentAssets', {}).get((year, quarter), {}).get('value')
            liab_val = all_data.get('Liabilities', {}).get((year, quarter), {}).get('value')
            curr_liab_val = all_data.get('CurrentLiabilities', {}).get((year, quarter), {}).get('value')
            equity_val = all_data.get('Equity', {}).get((year, quarter), {}).get('value')
            div_val = all_data.get('Dividend', {}).get((year, quarter), {}).get('value')
            
            # FCF 계산
            fcf_val = None
            if ocf_val and capex_val:
                fcf_val = ocf_val - abs(capex_val)
            
            # 날짜 (가장 신뢰할 수 있는 필드에서)
            fiscal_date = None
            for field_key in ['OCF', 'NetIncome', 'Revenue']:
                if field_key in all_data and (year, quarter) in all_data[field_key]:
                    fiscal_date = all_data[field_key][(year, quarter)].get('date')
                    if fiscal_date:
                        break
            
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
                    'operating_profit': op_val,
                    'total_assets': assets_val,
                    'current_assets': curr_assets_val,
                    'total_liabilities': liab_val,
                    'current_liabilities': curr_liab_val,
                    'total_equity': equity_val,
                    'dividend': abs(div_val) if div_val else None,
                    'data_source': 'EDGAR_COMPLETE',
                }
            )
            
            if created:
                saved_count += 1
            else:
                updated_count += 1
    
    if verbose:
        print(f"\n  OK 저장 완료: {saved_count}개 생성, {updated_count}개 업데이트")
    
    # 8. 품질 검증
    total_quarters = StockFinancialRaw.objects.filter(stock=stock).count()
    missing_ocf = StockFinancialRaw.objects.filter(stock=stock, ocf__isnull=True).count()
    missing_ni = StockFinancialRaw.objects.filter(stock=stock, net_income__isnull=True).count()
    missing_revenue = StockFinancialRaw.objects.filter(stock=stock, revenue__isnull=True).count()
    missing_capex = StockFinancialRaw.objects.filter(stock=stock, capex__isnull=True).count()
    
    if verbose:
        print(f"\n  품질 검증:")
        print(f"    - 총 분기: {total_quarters}")
        print(f"    - OCF 누락: {missing_ocf}")
        print(f"    - NetIncome 누락: {missing_ni}")
        print(f"    - Revenue 누락: {missing_revenue}")
        print(f"    - CAPEX 누락: {missing_capex}")
    
    # 필수 필드만 체크
    if missing_ocf == 0 and missing_ni == 0:
        if missing_revenue == 0 and missing_capex == 0:
            if verbose:
                print(f"\n  OK 품질 완벽")
            return True
        else:
            if verbose:
                print(f"\n  OK 품질 우수 (필수 필드 완벽, 일부 선택 필드 누락)")
            return True
    else:
        print(f"\n  ! 품질 불량 (필수 필드 누락)")
        return False


def main():
    """메인 함수"""
    
    # 주요 대형주 + 추가 종목
    TARGET_STOCKS = [
        # 테크
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
        # 금융
        'JPM', 'V', 'BAC', 'WFC',
        # 헬스케어
        'JNJ', 'UNH', 'PFE',
        # 소비재
        'WMT', 'PG', 'KO', 'PEP',
        # 에너지
        'XOM', 'CVX',
    ]
    
    print("\n" + "="*60)
    print(" EDGAR 완전 자동화 데이터 수집")
    print("="*60)
    print(f" 대상 종목: {len(TARGET_STOCKS)}개")
    print("="*60)
    
    success_count = 0
    failed_stocks = []
    
    for i, ticker in enumerate(TARGET_STOCKS, 1):
        print(f"\n[{i}/{len(TARGET_STOCKS)}] {ticker} 진행 중...")
        
        if collect_stock_data(ticker, verbose=True):
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
    print(f"  성공: {success_count}/{len(TARGET_STOCKS)}")
    print(f"  실패: {len(failed_stocks)}/{len(TARGET_STOCKS)}")
    
    if failed_stocks:
        print(f"\n  실패 종목: {', '.join(failed_stocks)}")
    
    print("="*60)
    
    # 최종 품질 확인
    print(f"\n 최종 품질 확인:")
    perfect_count = 0
    good_count = 0
    partial_count = 0
    
    for ticker in TARGET_STOCKS:
        try:
            stock = Stock.objects.get(stock_code=ticker)
            total = StockFinancialRaw.objects.filter(stock=stock).count()
            missing_ocf = StockFinancialRaw.objects.filter(stock=stock, ocf__isnull=True).count()
            missing_ni = StockFinancialRaw.objects.filter(stock=stock, net_income__isnull=True).count()
            missing_revenue = StockFinancialRaw.objects.filter(stock=stock, revenue__isnull=True).count()
            missing_capex = StockFinancialRaw.objects.filter(stock=stock, capex__isnull=True).count()
            
            if missing_ocf == 0 and missing_ni == 0 and missing_revenue == 0 and missing_capex == 0:
                print(f"  OK {ticker:6s} - {total}분기, 완벽")
                perfect_count += 1
            elif missing_ocf == 0 and missing_ni == 0:
                print(f"  O  {ticker:6s} - {total}분기, Revenue누락:{missing_revenue} CAPEX누락:{missing_capex}")
                good_count += 1
            else:
                print(f"  !  {ticker:6s} - {total}분기, OCF누락:{missing_ocf} NI누락:{missing_ni}")
                partial_count += 1
        except:
            print(f"  X  {ticker:6s} - 데이터 없음")
    
    print("\n" + "="*60)
    print(f"  완벽: {perfect_count}개")
    print(f"  우수: {good_count}개 (필수 필드 완벽)")
    print(f"  부분: {partial_count}개 (필수 필드 누락)")
    print("="*60)
    
    if perfect_count + good_count >= len(TARGET_STOCKS) * 0.8:
        print("\n  OK 데이터 품질 충분 - 포트폴리오 개발 진행 가능")
    else:
        print("\n  ! 데이터 품질 불충분 - 추가 보완 필요")


if __name__ == '__main__':
    main()

