"""
EDGAR 완벽 데이터 수집 시스템 (최종 버전)
- Fiscal year 관계없이 정확한 매칭
- 모든 10-Q, 10-K 데이터 수집
- 날짜 기준 자동 매칭
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
    ],
    
    'ICF': [
        'NetCashProvidedByUsedInInvestingActivities',
        'NetCashProvidedByUsedInInvestingActivitiesContinuingOperations',
    ],
    
    'CAPEX': [
        'PaymentsToAcquirePropertyPlantAndEquipment',
        'PaymentsToAcquireProductiveAssets',
        'PaymentsForCapitalImprovements',
    ],
    
    'NetIncome': [
        'NetIncomeLoss',
        'ProfitLoss',
        'NetIncomeLossAvailableToCommonStockholdersBasic',
    ],
    
    'Revenue': [
        'SalesRevenueNet',  # AAPL, JNJ
        'SalesRevenueGoodsNet',  # JNJ
        'Revenues',  # V, MSFT
        'RevenueFromContractWithCustomerExcludingAssessedTax',  # MSFT
        'RevenueFromContractWithCustomerIncludingAssessedTax',
        'SalesRevenueServicesNet',
    ],
    
    'OperatingProfit': [
        'OperatingIncomeLoss',
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments',
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
                print(f"  Rate limit, {wait_time}초 대기...")
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


def find_best_field(facts, field_names):
    """
    가장 데이터가 많은 필드 찾기
    """
    best_field = None
    max_count = 0
    
    for field_name in field_names:
        if field_name not in facts:
            continue
        
        units = facts[field_name].get('units', {}).get('USD', [])
        count = sum(1 for item in units if item.get('form') in ['10-Q', '10-K'])
        
        if count > max_count:
            max_count = count
            best_field = field_name
    
    return best_field, max_count


def extract_all_data_by_date(facts, field_name):
    """
    날짜 기준으로 모든 데이터 추출 (fiscal year 무관)
    반환: [(date, value, form), ...]
    """
    if field_name not in facts:
        return []
    
    result = []
    units = facts[field_name].get('units', {}).get('USD', [])
    
    for item in units:
        # 10-Q, 10-K만
        if item.get('form') not in ['10-Q', '10-K']:
            continue
        
        fiscal_date = item.get('end')
        value = item.get('val')
        form = item.get('form')
        
        if not fiscal_date or value is None:
            continue
        
        result.append((fiscal_date, value, form))
    
    # 날짜순 정렬 (최신순)
    result.sort(reverse=True)
    
    return result


def collect_stock_data(ticker, target_quarters=20):
    """
    종목 데이터 완벽 수집
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
    
    # 3. 각 필드별 최적 필드명 찾기
    print(f"\n  필드명 탐색:")
    field_mappings = {}
    
    for field_key, field_names in EDGAR_FIELDS.items():
        best_field, count = find_best_field(facts, field_names)
        
        if best_field:
            field_mappings[field_key] = best_field
            print(f"    OK {field_key:15s}: {best_field} ({count}개)")
    
    # 4. 필수 필드 체크
    required_fields = ['OCF', 'NetIncome']
    missing = [f for f in required_fields if f not in field_mappings]
    
    if missing:
        print(f"  X 필수 필드 없음: {', '.join(missing)}")
        return False
    
    # 5. 날짜 기준으로 데이터 추출
    print(f"\n  데이터 추출 중...")
    
    # 모든 필드의 데이터를 날짜 기준으로 추출
    all_field_data = {}
    for field_key, field_name in field_mappings.items():
        data_by_date = extract_all_data_by_date(facts, field_name)
        all_field_data[field_key] = {item[0]: item[1] for item in data_by_date[:target_quarters]}
    
    # 6. 모든 날짜 수집
    all_dates = set()
    for data_dict in all_field_data.values():
        all_dates.update(data_dict.keys())
    
    sorted_dates = sorted(all_dates, reverse=True)[:target_quarters]
    
    print(f"  발견된 분기: {len(sorted_dates)}개")
    
    # 7. DB 저장
    print(f"\n  DB 저장 중...")
    saved_count = 0
    updated_count = 0
    
    with transaction.atomic():
        for idx, fiscal_date in enumerate(sorted_dates, 1):
            # 날짜로 연도/분기 계산
            date_obj = datetime.strptime(fiscal_date, '%Y-%m-%d')
            year = date_obj.year
            month = date_obj.month
            
            # 분기 계산 (간단하게)
            if month in [1, 2, 3]:
                quarter = 1
            elif month in [4, 5, 6]:
                quarter = 2
            elif month in [7, 8, 9]:
                quarter = 3
            else:
                quarter = 4
            
            # 각 필드 값
            ocf_val = all_field_data.get('OCF', {}).get(fiscal_date)
            icf_val = all_field_data.get('ICF', {}).get(fiscal_date)
            capex_val = all_field_data.get('CAPEX', {}).get(fiscal_date)
            ni_val = all_field_data.get('NetIncome', {}).get(fiscal_date)
            rev_val = all_field_data.get('Revenue', {}).get(fiscal_date)
            op_val = all_field_data.get('OperatingProfit', {}).get(fiscal_date)
            assets_val = all_field_data.get('Assets', {}).get(fiscal_date)
            curr_assets_val = all_field_data.get('CurrentAssets', {}).get(fiscal_date)
            liab_val = all_field_data.get('Liabilities', {}).get(fiscal_date)
            curr_liab_val = all_field_data.get('CurrentLiabilities', {}).get(fiscal_date)
            equity_val = all_field_data.get('Equity', {}).get(fiscal_date)
            div_val = all_field_data.get('Dividend', {}).get(fiscal_date)
            
            # FCF 계산
            fcf_val = None
            if ocf_val and capex_val:
                fcf_val = ocf_val - abs(capex_val)
            
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
                    'data_source': 'EDGAR_PERFECT',
                }
            )
            
            if created:
                saved_count += 1
            else:
                updated_count += 1
    
    print(f"  OK 저장: {saved_count}개 생성, {updated_count}개 업데이트")
    
    # 8. 품질 검증
    print(f"\n  품질 검증:")
    total = StockFinancialRaw.objects.filter(stock=stock).count()
    missing_ocf = StockFinancialRaw.objects.filter(stock=stock, ocf__isnull=True).count()
    missing_ni = StockFinancialRaw.objects.filter(stock=stock, net_income__isnull=True).count()
    missing_revenue = StockFinancialRaw.objects.filter(stock=stock, revenue__isnull=True).count()
    missing_capex = StockFinancialRaw.objects.filter(stock=stock, capex__isnull=True).count()
    
    print(f"    총 분기: {total}")
    print(f"    OCF 누락: {missing_ocf}")
    print(f"    NetIncome 누락: {missing_ni}")
    print(f"    Revenue 누락: {missing_revenue}")
    print(f"    CAPEX 누락: {missing_capex}")
    
    if missing_ocf == 0 and missing_ni == 0 and missing_revenue == 0 and missing_capex == 0:
        print(f"\n  OK 완벽!")
        return True
    elif missing_ocf == 0 and missing_ni == 0:
        print(f"\n  O  우수 (필수 필드 완벽)")
        return True
    else:
        print(f"\n  ! 불량")
        return False


def main():
    """메인 함수"""
    
    # 테스트: Revenue 누락이 심한 종목들
    TARGET_STOCKS = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
        'META', 'TSLA', 'JPM', 'V', 'JNJ',
        'WMT', 'PG', 'XOM', 'CVX', 'KO',
        'BAC', 'WFC', 'UNH', 'PFE', 'PEP',
    ]
    
    print("\n" + "="*60)
    print(" EDGAR 완벽 데이터 수집 (Fiscal Year 대응)")
    print("="*60)
    print(f" 대상: {len(TARGET_STOCKS)}개")
    print("="*60)
    
    success = 0
    failed = []
    
    for i, ticker in enumerate(TARGET_STOCKS, 1):
        print(f"\n[{i}/{len(TARGET_STOCKS)}]")
        
        if collect_stock_data(ticker):
            success += 1
        else:
            failed.append(ticker)
        
        # Rate limit
        if i < len(TARGET_STOCKS):
            time.sleep(0.3)
    
    # 최종 요약
    print("\n" + "="*60)
    print(" 최종 요약")
    print("="*60)
    print(f"  성공: {success}/{len(TARGET_STOCKS)}")
    print(f"  실패: {len(failed)}/{len(TARGET_STOCKS)}")
    
    if failed:
        print(f"  실패: {', '.join(failed)}")
    
    print("="*60)
    
    # 상세 품질 확인
    print(f"\n 최종 품질 확인:")
    perfect = 0
    good = 0
    partial = 0
    
    for ticker in TARGET_STOCKS:
        try:
            stock = Stock.objects.get(stock_code=ticker)
            total = StockFinancialRaw.objects.filter(stock=stock).count()
            m_ocf = StockFinancialRaw.objects.filter(stock=stock, ocf__isnull=True).count()
            m_ni = StockFinancialRaw.objects.filter(stock=stock, net_income__isnull=True).count()
            m_rev = StockFinancialRaw.objects.filter(stock=stock, revenue__isnull=True).count()
            m_capex = StockFinancialRaw.objects.filter(stock=stock, capex__isnull=True).count()
            
            if m_ocf == 0 and m_ni == 0 and m_rev == 0 and m_capex == 0:
                print(f"  OK {ticker:6s} - {total}분기, 완벽")
                perfect += 1
            elif m_ocf == 0 and m_ni == 0:
                print(f"  O  {ticker:6s} - {total}분기, Rev:{m_rev} CAPEX:{m_capex}")
                good += 1
            else:
                print(f"  !  {ticker:6s} - {total}분기, OCF:{m_ocf} NI:{m_ni}")
                partial += 1
        except:
            print(f"  X  {ticker:6s} - 없음")
    
    print("\n" + "="*60)
    print(f"  완벽: {perfect}개")
    print(f"  우수: {good}개")
    print(f"  부분: {partial}개")
    print("="*60)
    
    if perfect >= len(TARGET_STOCKS) * 0.9:
        print("\n  OK 데이터 완벽! 포트폴리오 개발 진행")
    elif perfect + good >= len(TARGET_STOCKS) * 0.8:
        print("\n  OK 데이터 충분! 포트폴리오 개발 진행 가능")
    else:
        print("\n  ! 추가 보완 필요")


if __name__ == '__main__':
    main()

