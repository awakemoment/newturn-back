"""
누락된 데이터 보완 스크립트 (Revenue, CAPEX)
"""

import os
import sys
import django
import requests
from sec_cik_mapper import StockMapper
from datetime import datetime

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock, StockFinancialRaw
from django.db import transaction


# EDGAR 필드명 매핑 (더 많은 가능성 추가)
REVENUE_FIELDS = [
    'Revenues',
    'RevenueFromContractWithCustomerExcludingAssessedTax',
    'RevenueFromContractWithCustomerIncludingAssessedTax',
    'SalesRevenueNet',
    'SalesRevenueGoodsNet',
    'SalesRevenueServicesNet',
    'RevenuesNetOfInterestExpense',  # 금융주
    'InterestAndDividendIncomeOperating',  # 금융주
    'FinancialServicesRevenue',  # 금융주
]

CAPEX_FIELDS = [
    'PaymentsToAcquirePropertyPlantAndEquipment',  # 일반 기업
    'PaymentsForCapitalImprovements',
    'PaymentsToAcquireProductiveAssets',
    'PaymentsForProceedsFromOtherInvestingActivities',  # 금융주 (JPM 등)
    'PaymentsToAcquireBusinessesNetOfCashAcquired',  # 인수합병
]


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


def extract_quarterly_data(facts, field_names):
    """
    분기별 데이터 추출 (유연한 매칭)
    반환: {(year, quarter): value}
    """
    result = {}
    
    for field_name in field_names:
        if field_name not in facts:
            continue
        
        units = facts[field_name].get('units', {}).get('USD', [])
        
        for item in units:
            # 10-Q (분기) 또는 10-K (연간) 데이터만
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
            # 각 분기 종료월: 1-3월(Q1), 4-6월(Q2), 7-9월(Q3), 10-12월(Q4)
            # 하지만 회사마다 조금씩 다를 수 있음 (예: 1월 말, 2월 말, 3월 말 모두 Q1)
            if month in [1, 2, 3]:
                quarter = 1
            elif month in [4, 5, 6]:
                quarter = 2
            elif month in [7, 8, 9]:
                quarter = 3
            else:  # 10, 11, 12
                quarter = 4
            
            key = (year, quarter)
            
            # 같은 분기에 여러 값이 있으면 최신 값 또는 첫 번째 필드명의 값 우선
            if key not in result:
                result[key] = {
                    'value': value,
                    'date': fiscal_date,
                    'field': field_name
                }
            else:
                # 더 최신 데이터면 업데이트
                if fiscal_date > result[key]['date']:
                    result[key] = {
                        'value': value,
                        'date': fiscal_date,
                        'field': field_name
                    }
    
    return result


def fill_missing_data(ticker):
    """
    특정 종목의 누락된 Revenue, CAPEX 보완
    """
    print(f"\n {ticker} 데이터 보완 중...")
    
    # 1. Stock 조회
    try:
        stock = Stock.objects.get(stock_code=ticker)
    except Stock.DoesNotExist:
        print(f"  X DB에 종목 없음")
        return False
    
    # 2. 누락된 데이터 확인
    missing_revenue = StockFinancialRaw.objects.filter(
        stock=stock,
        revenue__isnull=True
    ).count()
    
    missing_capex = StockFinancialRaw.objects.filter(
        stock=stock,
        capex__isnull=True
    ).count()
    
    if missing_revenue == 0 and missing_capex == 0:
        print(f"  OK 누락 데이터 없음")
        return True
    
    print(f"  누락: Revenue {missing_revenue}개, CAPEX {missing_capex}개")
    
    # 3. EDGAR 데이터 가져오기
    edgar_data, error = get_edgar_data(ticker)
    if error:
        print(f"  X EDGAR 오류: {error}")
        return False
    
    facts = edgar_data.get('facts', {}).get('us-gaap', {})
    
    # 4. 분기별 데이터 추출
    revenue_data = extract_quarterly_data(facts, REVENUE_FIELDS)
    capex_data = extract_quarterly_data(facts, CAPEX_FIELDS)
    
    # 5. DB 업데이트
    updated_count = 0
    
    with transaction.atomic():
        financials = StockFinancialRaw.objects.filter(stock=stock).order_by(
            'disclosure_year', 'disclosure_quarter'
        )
        
        for financial in financials:
            key = (financial.disclosure_year, financial.disclosure_quarter)
            updated = False
            
            # Revenue 업데이트
            if financial.revenue is None and key in revenue_data:
                financial.revenue = revenue_data[key]['value']
                updated = True
                field_name = revenue_data[key].get('field', 'Unknown')
                print(f"    OK {key} Revenue: {revenue_data[key]['value']:,} (from {field_name})")
            
            # CAPEX 업데이트
            if financial.capex is None and key in capex_data:
                capex_val = abs(capex_data[key]['value'])  # 양수로 변환
                financial.capex = capex_val
                updated = True
                field_name = capex_data[key].get('field', 'Unknown')
                print(f"    OK {key} CAPEX: {capex_val:,} (from {field_name})")
                
                # FCF 재계산 (OCF가 있으면)
                if financial.ocf is not None:
                    financial.fcf = financial.ocf - capex_val
                    print(f"       -> FCF 재계산: {financial.fcf:,}")
            
            if updated:
                financial.save()
                updated_count += 1
    
    print(f"  OK {updated_count}개 분기 업데이트 완료")
    return True


def main():
    """누락 데이터 보완"""
    
    # 문제 있는 종목들
    STOCKS_TO_FIX = [
        'AAPL',   # Revenue 누락
        'MSFT',   # Revenue 누락
        'GOOGL',  # Revenue 누락
        'AMZN',   # CAPEX 누락
        'NVDA',   # CAPEX 누락
        'META',   # Revenue 누락
        'TSLA',   # Revenue 누락
        'JPM',    # 완료
        'V',      # Revenue 누락
        'JNJ',    # Revenue 누락
        'WMT',    # Revenue 누락
        'PG',     # Revenue 누락
        'XOM',    # 완벽
        'CVX',    # 완벽
        'KO',     # Revenue 누락
    ]
    
    print("\n" + "="*60)
    print(" 누락 데이터 보완 시작")
    print("="*60)
    
    success = 0
    failed = 0
    
    for ticker in STOCKS_TO_FIX:
        if fill_missing_data(ticker):
            success += 1
        else:
            failed += 1
    
    print("\n" + "="*60)
    print(f" 성공: {success}개")
    print(f" 실패: {failed}개")
    print("="*60)
    
    # 최종 확인
    print("\n 최종 확인:")
    for ticker in STOCKS_TO_FIX:
        try:
            stock = Stock.objects.get(stock_code=ticker)
            total = StockFinancialRaw.objects.filter(stock=stock).count()
            missing_revenue = StockFinancialRaw.objects.filter(stock=stock, revenue__isnull=True).count()
            missing_capex = StockFinancialRaw.objects.filter(stock=stock, capex__isnull=True).count()
            
            if missing_revenue == 0 and missing_capex == 0:
                status = "OK"
            else:
                status = "  "
            print(f"  {status} {ticker:6s} - Revenue 누락: {missing_revenue}/{total}, CAPEX 누락: {missing_capex}/{total}")
        except:
            pass


if __name__ == '__main__':
    main()

