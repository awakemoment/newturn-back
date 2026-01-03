"""
EDGAR 완벽 데이터 수집 (최종 버전)
- 순수 분기 데이터만 수집 (TTM, YTD 제외)
- start/end 날짜로 분기 판별
- 중복 제거
"""

import os
import sys
import django
import requests
from sec_cik_mapper import StockMapper
from datetime import datetime, timedelta
import time

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock, StockFinancialRaw
from django.db import transaction


# 모든 가능한 EDGAR 필드명
EDGAR_FIELDS = {
    'OCF': [
        'NetCashProvidedByUsedInOperatingActivities',
        'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations',
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
        'SalesRevenueNet',
        'SalesRevenueGoodsNet',
        'Revenues',
        'RevenueFromContractWithCustomerExcludingAssessedTax',
        'RevenueFromContractWithCustomerIncludingAssessedTax',
    ],
    
    'OperatingProfit': [
        'OperatingIncomeLoss',
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
                time.sleep(wait_time)
                continue
            else:
                return None, None, f"HTTP {response.status_code}"
                
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
            else:
                return None, None, str(e)
    
    return None, None, "Max retries"


def is_quarterly_data(start_date, end_date):
    """
    순수 분기 데이터인지 확인 (TTM, YTD 제외)
    """
    if not start_date or not end_date:
        return False
    
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # 기간 계산
        days = (end - start).days
        
        # 분기는 대략 80-100일 (3개월)
        # 너무 길면 TTM (365일) 또는 YTD
        if 70 <= days <= 110:
            return True
        
        return False
        
    except:
        return False


def find_best_field(facts, field_names):
    """가장 데이터가 많은 필드 찾기"""
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


def extract_quarterly_data(facts, field_name):
    """
    순수 분기 데이터만 추출 (예전 방식 적용)
    반환: [(end_date, value), ...]
    """
    if field_name not in facts:
        return []
    
    result = []
    units = facts[field_name].get('units', {}).get('USD', [])
    seen_dates = set()
    
    for item in units:
        # 10-Q, 10-K만
        if item.get('form') not in ['10-Q', '10-K']:
            continue
        
        end_date = item.get('end')
        start_date = item.get('start')
        value = item.get('val')
        
        if not end_date or value is None:
            continue
        
        # 핵심: start 날짜가 반드시 있어야 함!
        # start 없으면 TTM이거나 시점 데이터
        if not start_date:
            continue
        
        # 이미 처리한 날짜면 건너뛰기
        if end_date in seen_dates:
            continue
        
        # 분기 기간 체크 (약 3개월)
        if not is_quarterly_data(start_date, end_date):
            continue
        
        result.append((end_date, value))
        seen_dates.add(end_date)
    
    # 날짜순 정렬 (최신순)
    result.sort(reverse=True)
    
    return result


def extract_balance_sheet_data(facts, field_name):
    """
    재무상태표 데이터 추출 (시점 데이터)
    반환: [(date, value), ...]
    """
    if field_name not in facts:
        return []
    
    result = []
    units = facts[field_name].get('units', {}).get('USD', [])
    seen_dates = set()
    
    for item in units:
        # 10-Q, 10-K만
        if item.get('form') not in ['10-Q', '10-K']:
            continue
        
        end_date = item.get('end')
        value = item.get('val')
        
        if not end_date or value is None:
            continue
        
        # 중복 제거
        if end_date in seen_dates:
            continue
        
        result.append((end_date, value))
        seen_dates.add(end_date)
    
    # 날짜순 정렬 (최신순)
    result.sort(reverse=True)
    
    return result


def collect_stock_data(ticker, target_quarters=20):
    """종목 데이터 완벽 수집"""
    
    print(f"\n============================================================")
    print(f" {ticker} 수집")
    print(f"============================================================")
    
    # 1. Stock 조회
    try:
        stock = Stock.objects.get(stock_code=ticker)
    except Stock.DoesNotExist:
        print(f"  X 종목 없음")
        return False
    
    # 2. EDGAR 데이터
    print(f"  API 조회 중...")
    full_data, facts, error = get_edgar_data(ticker)
    
    if error:
        print(f"  X {error}")
        return False
    
    print(f"  OK 데이터 획득")
    
    # 3. 필드명 찾기
    field_mappings = {}
    
    for field_key, field_names in EDGAR_FIELDS.items():
        best_field, count = find_best_field(facts, field_names)
        if best_field:
            field_mappings[field_key] = best_field
    
    print(f"  OK 필드: {len(field_mappings)}개")
    
    # 4. 필수 필드 체크
    if 'OCF' not in field_mappings or 'NetIncome' not in field_mappings:
        print(f"  X 필수 필드 없음")
        return False
    
    # 5. 데이터 추출 (기간 데이터 vs 시점 데이터 구분)
    print(f"  데이터 추출 중...")
    
    # 기간 데이터 (손익계산서, 현금흐름표)
    period_fields = ['OCF', 'ICF', 'CAPEX', 'NetIncome', 'Revenue', 'OperatingProfit', 'Dividend']
    all_period_data = {}
    
    for field_key in period_fields:
        if field_key in field_mappings:
            data = extract_quarterly_data(facts, field_mappings[field_key])
            all_period_data[field_key] = {item[0]: item[1] for item in data[:target_quarters]}
    
    # 시점 데이터 (재무상태표)
    balance_fields = ['Assets', 'CurrentAssets', 'Liabilities', 'CurrentLiabilities', 'Equity']
    all_balance_data = {}
    
    for field_key in balance_fields:
        if field_key in field_mappings:
            data = extract_balance_sheet_data(facts, field_mappings[field_key])
            all_balance_data[field_key] = {item[0]: item[1] for item in data[:target_quarters]}
    
    # 6. 모든 날짜 수집 (기간 데이터 기준)
    all_dates = set()
    for data_dict in all_period_data.values():
        all_dates.update(data_dict.keys())
    
    sorted_dates = sorted(all_dates, reverse=True)[:target_quarters]
    
    print(f"  OK 분기: {len(sorted_dates)}개")
    
    # 7. DB 저장
    saved = 0
    updated = 0
    
    with transaction.atomic():
        for fiscal_date in sorted_dates:
            # 날짜 파싱
            date_obj = datetime.strptime(fiscal_date, '%Y-%m-%d')
            year = date_obj.year
            month = date_obj.month
            
            # 분기 계산
            if month in [1, 2, 3]:
                quarter = 1
            elif month in [4, 5, 6]:
                quarter = 2
            elif month in [7, 8, 9]:
                quarter = 3
            else:
                quarter = 4
            
            # 각 필드 값
            ocf = all_period_data.get('OCF', {}).get(fiscal_date)
            icf = all_period_data.get('ICF', {}).get(fiscal_date)
            capex = all_period_data.get('CAPEX', {}).get(fiscal_date)
            ni = all_period_data.get('NetIncome', {}).get(fiscal_date)
            rev = all_period_data.get('Revenue', {}).get(fiscal_date)
            op = all_period_data.get('OperatingProfit', {}).get(fiscal_date)
            div = all_period_data.get('Dividend', {}).get(fiscal_date)
            
            # 재무상태표 (가장 가까운 날짜)
            assets = all_balance_data.get('Assets', {}).get(fiscal_date)
            curr_assets = all_balance_data.get('CurrentAssets', {}).get(fiscal_date)
            liab = all_balance_data.get('Liabilities', {}).get(fiscal_date)
            curr_liab = all_balance_data.get('CurrentLiabilities', {}).get(fiscal_date)
            equity = all_balance_data.get('Equity', {}).get(fiscal_date)
            
            # FCF 계산
            fcf = None
            if ocf and capex:
                fcf = ocf - abs(capex)
            
            # 저장
            financial, created = StockFinancialRaw.objects.update_or_create(
                stock=stock,
                disclosure_year=year,
                disclosure_quarter=quarter,
                defaults={
                    'disclosure_date': fiscal_date,
                    'ocf': ocf,
                    'icf': icf,
                    'capex': abs(capex) if capex else None,
                    'fcf': fcf,
                    'net_income': ni,
                    'revenue': rev,
                    'operating_profit': op,
                    'total_assets': assets,
                    'current_assets': curr_assets,
                    'total_liabilities': liab,
                    'current_liabilities': curr_liab,
                    'total_equity': equity,
                    'dividend': abs(div) if div else None,
                    'data_source': 'EDGAR_FINAL',
                }
            )
            
            if created:
                saved += 1
            else:
                updated += 1
    
    print(f"  OK 저장: {saved}개 생성, {updated}개 업데이트")
    
    # 8. 품질 검증
    total = StockFinancialRaw.objects.filter(stock=stock).count()
    m_ocf = StockFinancialRaw.objects.filter(stock=stock, ocf__isnull=True).count()
    m_ni = StockFinancialRaw.objects.filter(stock=stock, net_income__isnull=True).count()
    m_rev = StockFinancialRaw.objects.filter(stock=stock, revenue__isnull=True).count()
    m_capex = StockFinancialRaw.objects.filter(stock=stock, capex__isnull=True).count()
    
    print(f"\n  품질: 총{total}, OCF:{m_ocf} NI:{m_ni} Rev:{m_rev} CAPEX:{m_capex}")
    
    if m_ocf == 0 and m_ni == 0 and m_rev == 0 and m_capex == 0:
        print(f"  OK 완벽!")
        return True
    elif m_ocf == 0 and m_ni == 0:
        print(f"  O  우수")
        return True
    else:
        print(f"  ! 불량")
        return False


def main():
    """메인"""
    
    TARGET_STOCKS = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
        'META', 'TSLA', 'JPM', 'V', 'JNJ',
        'WMT', 'PG', 'XOM', 'CVX', 'KO',
        'BAC', 'WFC', 'UNH', 'PFE', 'PEP',
    ]
    
    print("\n" + "="*60)
    print(" EDGAR 완벽 수집 (분기 데이터만)")
    print("="*60)
    
    success = 0
    failed = []
    
    for i, ticker in enumerate(TARGET_STOCKS, 1):
        print(f"\n[{i}/{len(TARGET_STOCKS)}]")
        
        if collect_stock_data(ticker):
            success += 1
        else:
            failed.append(ticker)
        
        time.sleep(0.3)
    
    # 요약
    print("\n" + "="*60)
    print(" 요약")
    print("="*60)
    print(f"  성공: {success}/{len(TARGET_STOCKS)}")
    
    # 상세 품질
    print(f"\n 품질 확인:")
    perfect = 0
    good = 0
    
    for ticker in TARGET_STOCKS:
        try:
            stock = Stock.objects.get(stock_code=ticker)
            total = StockFinancialRaw.objects.filter(stock=stock).count()
            m_ocf = StockFinancialRaw.objects.filter(stock=stock, ocf__isnull=True).count()
            m_ni = StockFinancialRaw.objects.filter(stock=stock, net_income__isnull=True).count()
            m_rev = StockFinancialRaw.objects.filter(stock=stock, revenue__isnull=True).count()
            m_capex = StockFinancialRaw.objects.filter(stock=stock, capex__isnull=True).count()
            
            if m_ocf == 0 and m_ni == 0 and m_rev == 0 and m_capex == 0:
                print(f"  OK {ticker:6s} - {total}분기 완벽")
                perfect += 1
            elif m_ocf == 0 and m_ni == 0:
                print(f"  O  {ticker:6s} - {total}분기 우수 (Rev:{m_rev} CAPEX:{m_capex})")
                good += 1
            else:
                print(f"  !  {ticker:6s} - {total}분기 불량 (OCF:{m_ocf} NI:{m_ni})")
        except:
            print(f"  X  {ticker:6s} - 없음")
    
    print("\n" + "="*60)
    print(f"  완벽: {perfect}개")
    print(f"  우수: {good}개 (필수 필드 OK)")
    print("="*60)


if __name__ == '__main__':
    main()

