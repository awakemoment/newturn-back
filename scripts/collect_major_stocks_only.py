"""
주요 대형주만 재무 데이터 수집
"""

import os
import sys
import django
from datetime import datetime
import time

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from sec_edgar_api import EdgarClient
from apps.stocks.models import Stock, StockFinancialRaw
from django.db import transaction

# EDGAR 클라이언트
edgar = EdgarClient(user_agent="newturn support@awakemoment.io")


def parse_date(date_str):
    """날짜 파싱"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return None


def determine_quarter(end_date):
    """분기 판단"""
    month = end_date.month
    if month in [1, 2, 3]:
        return 1
    elif month in [4, 5, 6]:
        return 2
    elif month in [7, 8, 9]:
        return 3
    else:
        return 4


def extract_latest_value(units_data, unit='USD'):
    """
    최신 값 추출 (중복 제거)
    """
    if unit not in units_data:
        return []
    
    data_list = units_data[unit]
    sorted_data = sorted(data_list, key=lambda x: x.get('end', ''), reverse=True)
    
    recent_data = []
    seen_quarters = set()
    
    for item in sorted_data:
        end_date_str = item.get('end')
        if not end_date_str:
            continue
        
        end_date = parse_date(end_date_str)
        if not end_date:
            continue
        
        year = end_date.year
        quarter = determine_quarter(end_date)
        key = f"{year}Q{quarter}"
        
        # 중복 제거
        if key not in seen_quarters:
            recent_data.append({
                'year': year,
                'quarter': quarter,
                'date': end_date,
                'value': item.get('val'),
            })
            seen_quarters.add(key)
        
        if len(recent_data) >= 20:
            break
    
    return recent_data


def collect_stock(ticker):
    """종목 데이터 수집"""
    
    print(f"\n{'='*60}")
    print(f" {ticker}")
    print(f"{'='*60}")
    
    # Stock 조회
    try:
        stock = Stock.objects.get(stock_code=ticker)
    except Stock.DoesNotExist:
        print(f"  X 종목 없음")
        return False
    
    # EDGAR 조회
    try:
        print(f"  API 조회...")
        time.sleep(0.2)
        
        facts = edgar.get_company_facts(cik=stock.corp_code)
        
        if 'facts' not in facts or 'us-gaap' not in facts['facts']:
            print(f"  X US-GAAP 없음")
            return False
        
        us_gaap = facts['facts']['us-gaap']
        
    except Exception as e:
        print(f"  X 오류: {e}")
        return False
    
    # 필드명 (여러 가능성)
    items_map = {
        'ocf': ['NetCashProvidedByUsedInOperatingActivities'],
        'icf': ['NetCashProvidedByUsedInInvestingActivities'],
        'capex': ['PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets'],
        'net_income': ['NetIncomeLoss'],
        'total_assets': ['Assets'],
        'total_liabilities': ['Liabilities'],
        'total_equity': ['StockholdersEquity', 'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'],
        'revenue': ['SalesRevenueNet', 'SalesRevenueGoodsNet', 'Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax'],
    }
    
    # 데이터 추출
    extracted = {}
    for key, gaap_names in items_map.items():
        data = []
        for gaap_name in gaap_names:
            if gaap_name in us_gaap:
                data = extract_latest_value(us_gaap[gaap_name]['units'])
                if data:
                    break
        extracted[key] = data
    
    # OCF 필수
    if not extracted.get('ocf'):
        print(f"  X OCF 없음")
        return False
    
    print(f"  OK 데이터 추출: {len(extracted['ocf'])}개 분기")
    
    # DB 저장
    financials_to_create = []
    
    for ocf_item in extracted['ocf']:
        year = ocf_item['year']
        quarter = ocf_item['quarter']
        end_date = ocf_item['date']
        
        # 같은 분기 데이터 찾기
        icf_match = next((x for x in extracted.get('icf', []) if x['year'] == year and x['quarter'] == quarter), None)
        capex_match = next((x for x in extracted.get('capex', []) if x['year'] == year and x['quarter'] == quarter), None)
        ni_match = next((x for x in extracted.get('net_income', []) if x['year'] == year and x['quarter'] == quarter), None)
        rev_match = next((x for x in extracted.get('revenue', []) if x['year'] == year and x['quarter'] == quarter), None)
        assets_match = next((x for x in extracted.get('total_assets', []) if x['year'] == year and x['quarter'] == quarter), None)
        liab_match = next((x for x in extracted.get('total_liabilities', []) if x['year'] == year and x['quarter'] == quarter), None)
        equity_match = next((x for x in extracted.get('total_equity', []) if x['year'] == year and x['quarter'] == quarter), None)
        
        # FCF 계산
        fcf_val = None
        if capex_match:
            fcf_val = ocf_item['value'] - abs(capex_match['value'])
        
        financials_to_create.append(StockFinancialRaw(
            stock=stock,
            disclosure_year=year,
            disclosure_quarter=quarter,
            disclosure_date=end_date,
            ocf=ocf_item['value'],
            icf=icf_match['value'] if icf_match else None,
            capex=abs(capex_match['value']) if capex_match else None,
            fcf=fcf_val,
            net_income=ni_match['value'] if ni_match else None,
            revenue=rev_match['value'] if rev_match else None,
            total_assets=assets_match['value'] if assets_match else None,
            total_liabilities=liab_match['value'] if liab_match else None,
            total_equity=equity_match['value'] if equity_match else None,
            data_source='EDGAR',
        ))
    
    # Bulk create
    with transaction.atomic():
        # 기존 데이터 삭제
        StockFinancialRaw.objects.filter(stock=stock).delete()
        
        # 새로 저장
        StockFinancialRaw.objects.bulk_create(financials_to_create)
    
    print(f"  OK 저장: {len(financials_to_create)}개 분기")
    
    # 품질 확인
    total = StockFinancialRaw.objects.filter(stock=stock).count()
    m_rev = StockFinancialRaw.objects.filter(stock=stock, revenue__isnull=True).count()
    m_capex = StockFinancialRaw.objects.filter(stock=stock, capex__isnull=True).count()
    
    print(f"  품질: 총{total}, Revenue누락:{m_rev}, CAPEX누락:{m_capex}")
    
    return True


def main():
    """메인"""
    
    # 주요 대형주
    TARGET_STOCKS = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
        'META', 'TSLA', 'JPM', 'V', 'JNJ',
        'WMT', 'PG', 'XOM', 'CVX', 'KO',
    ]
    
    print("\n" + "="*60)
    print(" 주요 종목 재무 데이터 수집")
    print("="*60)
    
    success = 0
    failed = []
    
    for i, ticker in enumerate(TARGET_STOCKS, 1):
        print(f"\n[{i}/{len(TARGET_STOCKS)}]")
        
        if collect_stock(ticker):
            success += 1
        else:
            failed.append(ticker)
        
        time.sleep(0.3)
    
    # 요약
    print("\n" + "="*60)
    print(" 요약")
    print("="*60)
    print(f"  성공: {success}/{len(TARGET_STOCKS)}")
    
    if failed:
        print(f"  실패: {', '.join(failed)}")
    
    # 최종 품질
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
                print(f"  !  {ticker:6s} - {total}분기 불량")
        except:
            print(f"  X  {ticker:6s} - 없음")
    
    print("\n" + "="*60)
    print(f"  완벽: {perfect}개")
    print(f"  우수: {good}개")
    print("="*60)
    
    if perfect + good >= len(TARGET_STOCKS) * 0.8:
        print("\n  OK 데이터 충분! 포트폴리오 개발 진행 가능")


if __name__ == '__main__':
    main()

