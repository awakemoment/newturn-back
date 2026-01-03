"""
개선된 EDGAR 재무 데이터 수집 스크립트 v2
- 완벽한 필드명 매핑
- 자동 검증
- 상세 로깅
- 재시도 로직
"""

import os
import sys
import django
import requests
from sec_cik_mapper import StockMapper
from datetime import datetime
import time
import logging

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock, StockFinancialRaw
from django.db import transaction

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ========================================
# EDGAR 필드명 매핑 (우선순위 순서)
# ========================================

FIELD_MAPPINGS = {
    'OCF': [
        'NetCashProvidedByUsedInOperatingActivities',
        'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations',
        'CashProvidedByUsedInOperatingActivities',
        'NetCashFromOperatingActivities',
    ],
    
    'CAPEX': [
        'PaymentsToAcquirePropertyPlantAndEquipment',
        'PaymentsForCapitalImprovements',
        'PaymentsToAcquireProductiveAssets',
        'CapitalExpendituresIncurredButNotYetPaid',
    ],
    
    'ICF': [
        'NetCashProvidedByUsedInInvestingActivities',
        'NetCashProvidedByUsedInInvestingActivitiesContinuingOperations',
        'CashProvidedByUsedInInvestingActivities',
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
    
    'OperatingProfit': [
        'OperatingIncomeLoss',
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',
    ],
    
    'Assets': [
        'Assets',
        'AssetsCurrent',
    ],
    
    'CurrentAssets': [
        'AssetsCurrent',
    ],
    
    'Liabilities': [
        'Liabilities',
        'LiabilitiesAndStockholdersEquity',
    ],
    
    'CurrentLiabilities': [
        'LiabilitiesCurrent',
    ],
    
    'TotalLiabilities': [
        'Liabilities',
        'LiabilitiesNoncurrent',
    ],
    
    'Equity': [
        'StockholdersEquity',
        'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest',
        'ShareholdersEquity',
    ],
    
    'Dividend': [
        'PaymentsOfDividends',
        'PaymentsOfDividendsCommonStock',
        'DividendsCash',
    ],
}


def get_edgar_data(ticker, retries=3):
    """EDGAR API에서 데이터 가져오기 (재시도 포함)"""
    for attempt in range(retries):
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
            elif response.status_code == 429:  # Rate limit
                wait_time = 2 ** attempt
                logger.warning(f"  ⚠️ Rate limit, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                return None, f"HTTP {response.status_code}"
                
        except Exception as e:
            if attempt < retries - 1:
                logger.warning(f"  ⚠️ Attempt {attempt + 1} failed, retrying...")
                time.sleep(1)
            else:
                return None, str(e)
    
    return None, "Max retries exceeded"


def extract_quarterly_value(facts, field_names, fiscal_year, fiscal_quarter):
    """
    특정 분기의 값을 추출 (TTM 제외, 순수 분기 데이터만)
    """
    target_month_map = {
        1: [1, 2, 3],      # Q1: Jan-Mar
        2: [4, 5, 6],      # Q2: Apr-Jun
        3: [7, 8, 9],      # Q3: Jul-Sep
        4: [10, 11, 12],   # Q4: Oct-Dec
    }
    
    target_months = target_month_map.get(fiscal_quarter, [])
    
    for field_name in field_names:
        if field_name not in facts:
            continue
        
        units = facts[field_name].get('units', {}).get('USD', [])
        
        for item in units:
            # 10-Q (분기) 또는 10-K (연간) 데이터만
            form = item.get('form')
            if form not in ['10-Q', '10-K']:
                continue
            
            # 날짜 확인
            end_date = item.get('end')
            if not end_date:
                continue
            
            date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            
            # 연도 확인
            if date_obj.year != fiscal_year:
                continue
            
            # 분기 확인 (월로)
            if date_obj.month not in target_months:
                continue
            
            # fp (fiscal period) 확인 - Q1, Q2, Q3, FY 등
            fp = item.get('fp')
            
            # FY는 Q4로 간주
            if fp == 'FY' and fiscal_quarter != 4:
                continue
            
            # 값 반환
            value = item.get('val')
            if value is not None:
                logger.debug(f"    → {field_name}: {value:,} (form: {form}, fp: {fp}, date: {end_date})")
                return value, field_name
    
    return None, None


def collect_stock_financials(ticker, update_existing=False):
    """
    특정 종목의 재무 데이터 수집
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"📊 {ticker} 데이터 수집 시작")
    logger.info(f"{'='*60}")
    
    # 1. Stock 조회
    try:
        stock = Stock.objects.get(stock_code=ticker)
    except Stock.DoesNotExist:
        logger.error(f"  ❌ DB에 종목 없음")
        return False, "Stock not found"
    
    # 2. EDGAR 데이터 가져오기
    edgar_data, error = get_edgar_data(ticker)
    if error:
        logger.error(f"  ❌ EDGAR 오류: {error}")
        return False, error
    
    logger.info(f"  ✅ EDGAR 데이터 획득")
    
    facts = edgar_data.get('facts', {}).get('us-gaap', {})
    
    # 3. 모든 분기 데이터 수집
    all_quarters = get_all_quarters_from_edgar(facts)
    
    if not all_quarters:
        logger.warning(f"  ⚠️ 분기 데이터 없음")
        return False, "No quarterly data"
    
    logger.info(f"  📅 발견된 분기: {len(all_quarters)}개")
    
    # 4. 각 분기별로 데이터 수집
    collected_count = 0
    updated_count = 0
    failed_quarters = []
    
    with transaction.atomic():
        for (year, quarter, fiscal_date) in sorted(all_quarters, reverse=True)[:20]:  # 최근 20분기
            logger.info(f"\n  📈 {year}Q{quarter} ({fiscal_date}) 처리 중...")
            
            # 각 필드 수집
            field_values = {}
            field_sources = {}
            
            for field_key, field_names in FIELD_MAPPINGS.items():
                value, source = extract_quarterly_value(facts, field_names, year, quarter)
                field_values[field_key] = value
                field_sources[field_key] = source
                
                if value is not None:
                    logger.debug(f"    ✅ {field_key}: {value:,} (from {source})")
                else:
                    logger.debug(f"    ⚠️ {field_key}: 없음")
            
            # FCF 계산
            if field_values['OCF'] and field_values['CAPEX']:
                field_values['FCF'] = field_values['OCF'] - abs(field_values['CAPEX'])
                logger.debug(f"    💰 FCF 계산: {field_values['FCF']:,}")
            
            # DB 저장
            financial, created = StockFinancialRaw.objects.update_or_create(
                stock=stock,
                disclosure_year=year,
                disclosure_quarter=quarter,
                defaults={
                    'disclosure_date': fiscal_date,
                    'ocf': field_values.get('OCF'),
                    'icf': field_values.get('ICF'),
                    'fcf': field_values.get('FCF'),
                    'capex': abs(field_values.get('CAPEX')) if field_values.get('CAPEX') else None,
                    'net_income': field_values.get('NetIncome'),
                    'revenue': field_values.get('Revenue'),
                    'operating_profit': field_values.get('OperatingProfit'),
                    'total_assets': field_values.get('Assets'),
                    'current_assets': field_values.get('CurrentAssets'),
                    'current_liabilities': field_values.get('CurrentLiabilities'),
                    'total_liabilities': field_values.get('TotalLiabilities'),
                    'total_equity': field_values.get('Equity'),
                    'dividend': abs(field_values.get('Dividend')) if field_values.get('Dividend') else None,
                    'data_source': 'EDGAR_V2',
                }
            )
            
            if created:
                collected_count += 1
                logger.info(f"    ✅ 생성 완료")
            else:
                updated_count += 1
                logger.info(f"    ✅ 업데이트 완료")
            
            # 필수 필드 검증
            missing_critical = []
            if not field_values.get('OCF'):
                missing_critical.append('OCF')
            if not field_values.get('NetIncome'):
                missing_critical.append('NetIncome')
            
            if missing_critical:
                failed_quarters.append((year, quarter, missing_critical))
                logger.warning(f"    ⚠️ 필수 필드 누락: {', '.join(missing_critical)}")
    
    # 5. 결과 요약
    logger.info(f"\n{'='*60}")
    logger.info(f"✅ {ticker} 수집 완료")
    logger.info(f"  - 생성: {collected_count}분기")
    logger.info(f"  - 업데이트: {updated_count}분기")
    if failed_quarters:
        logger.warning(f"  ⚠️ 필수 필드 누락: {len(failed_quarters)}분기")
        for year, quarter, missing in failed_quarters:
            logger.warning(f"    - {year}Q{quarter}: {', '.join(missing)}")
    logger.info(f"{'='*60}")
    
    return True, None


def get_all_quarters_from_edgar(facts):
    """
    EDGAR 데이터에서 모든 분기 목록 추출
    """
    quarters = set()
    
    # OCF 필드에서 분기 목록 추출
    for field_name in FIELD_MAPPINGS['OCF']:
        if field_name not in facts:
            continue
        
        units = facts[field_name].get('units', {}).get('USD', [])
        
        for item in units:
            if item.get('form') not in ['10-Q', '10-K']:
                continue
            
            end_date = item.get('end')
            if not end_date:
                continue
            
            date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            year = date_obj.year
            month = date_obj.month
            quarter = (month - 1) // 3 + 1
            
            quarters.add((year, quarter, end_date))
    
    return quarters


def main():
    """메인 함수"""
    
    # 테스트할 주요 종목
    TEST_STOCKS = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
        'META', 'TSLA', 'JPM', 'V', 'JNJ',
    ]
    
    logger.info("\n" + "="*60)
    logger.info("🚀 개선된 EDGAR 데이터 수집 v2 시작")
    logger.info("="*60)
    
    success_count = 0
    failed_stocks = []
    
    for ticker in TEST_STOCKS:
        success, error = collect_stock_financials(ticker)
        
        if success:
            success_count += 1
        else:
            failed_stocks.append((ticker, error))
        
        # API Rate limit 고려
        time.sleep(0.2)
    
    # 최종 요약
    logger.info("\n" + "="*60)
    logger.info("📊 최종 요약")
    logger.info("="*60)
    logger.info(f"  ✅ 성공: {success_count}/{len(TEST_STOCKS)}")
    logger.info(f"  ❌ 실패: {len(failed_stocks)}/{len(TEST_STOCKS)}")
    
    if failed_stocks:
        logger.error(f"\n  실패 종목:")
        for ticker, error in failed_stocks:
            logger.error(f"    - {ticker}: {error}")
    
    logger.info("="*60)


if __name__ == '__main__':
    main()

