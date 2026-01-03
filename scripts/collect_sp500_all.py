"""
S&P 500 전체 종목 재무 데이터 수집

사용법:
    python scripts/collect_sp500_all.py

주의:
    - SEC API Rate Limit: 10 requests/second
    - 500개 종목 수집 시 약 50분 소요 예상
"""
import os
import sys
import django
import time
import requests
from datetime import datetime

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock, StockFinancialRaw

# SEC API User Agent
USER_AGENT = "Newturn support@newturn.com"


def get_sp500_tickers():
    """
    S&P 500 종목 목록 가져오기 (Wikipedia)
    """
    print("\n" + "="*60)
    print("📋 S&P 500 종목 목록 가져오는 중...")
    print("="*60)
    
    import pandas as pd
    
    try:
        # Wikipedia에서 S&P 500 목록 가져오기
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        
        # User-Agent 헤더 추가 (403 방지)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        tables = pd.read_html(url, storage_options={'User-Agent': headers['User-Agent']})
        sp500_table = tables[0]
        
        tickers = sp500_table['Symbol'].tolist()
        
        # 특수 문자 처리 (예: BRK.B -> BRK-B)
        tickers = [ticker.replace('.', '-') for ticker in tickers]
        
        print(f"✅ S&P 500 종목 {len(tickers)}개 가져옴")
        return tickers
        
    except Exception as e:
        print(f"❌ S&P 500 목록 가져오기 실패: {e}")
        print("   대체 방법: 주요 종목만 수집합니다...")
        # 대체 리스트 (시가총액 상위 50개)
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'UNH', 'JNJ',
            'V', 'WMT', 'JPM', 'MA', 'PG', 'XOM', 'HD', 'CVX', 'MRK', 'ABBV',
            'KO', 'PEP', 'COST', 'AVGO', 'TMO', 'MCD', 'CSCO', 'ACN', 'ABT', 'ADBE',
            'NKE', 'LLY', 'DHR', 'TXN', 'NEE', 'PM', 'VZ', 'UPS', 'CRM', 'ORCL',
            'QCOM', 'HON', 'IBM', 'AMGN', 'INTU', 'LOW', 'UNP', 'CAT', 'GE', 'AMD'
        ]


def get_cik_from_ticker(ticker):
    """티커로 CIK 찾기"""
    try:
        url = "https://www.sec.gov/files/company_tickers_exchange.json"
        headers = {"User-Agent": USER_AGENT}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        companies = response.json()
        
        # 티커로 검색
        for item in companies.get('data', []):
            if len(item) >= 3 and item[2] == ticker:
                cik = str(item[0]).zfill(10)
                return cik
        
        return None
        
    except Exception as e:
        print(f"   ⚠️ CIK 조회 실패: {e}")
        return None


def collect_stock_data(ticker, cik):
    """종목 재무 데이터 수집"""
    try:
        # EDGAR Company Facts API
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        headers = {"User-Agent": USER_AGENT}
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 404:
            return None, "404 Not Found"
        
        response.raise_for_status()
        company_data = response.json()
        
        # Stock 객체 가져오기 또는 생성
        stock, created = Stock.objects.get_or_create(
            stock_code=ticker,
            defaults={
                'stock_name': company_data.get('entityName', ticker),
                'stock_name_en': company_data.get('entityName', ticker),
                'exchange': 'nasdaq',  # 기본값
                'country': 'us',
                'cik': cik,
            }
        )
        
        # 재무 데이터 추출 및 저장
        us_gaap = company_data.get('facts', {}).get('us-gaap', {})
        
        if not us_gaap:
            return stock, "No GAAP data"
        
        # 데이터 수집
        collected_count = extract_and_save_financials(stock, us_gaap)
        
        return stock, f"Success: {collected_count} quarters"
        
    except requests.exceptions.Timeout:
        return None, "Timeout"
    except requests.exceptions.RequestException as e:
        return None, f"Request Error: {str(e)[:50]}"
    except Exception as e:
        return None, f"Error: {str(e)[:50]}"


def extract_and_save_financials(stock, us_gaap):
    """재무 데이터 추출 및 저장"""
    # 수집할 항목
    items_map = {
        'ocf': ['NetCashProvidedByUsedInOperatingActivities'],
        'capex': ['PaymentsToAcquirePropertyPlantAndEquipment', 
                  'PaymentsToAcquireProductiveAssets',
                  'PaymentsForProceedsFromOtherInvestingActivities'],
        'net_income': ['NetIncomeLoss', 'ProfitLoss'],
        'total_assets': ['Assets'],
        'total_liabilities': ['Liabilities'],
        'total_equity': ['StockholdersEquity'],
        'revenue': ['SalesRevenueNet', 'Revenues', 
                    'RevenueFromContractWithCustomerExcludingAssessedTax'],
    }
    
    # 각 항목별 데이터 추출
    extracted = {}
    for key, gaap_names in items_map.items():
        data = []
        for gaap_name in gaap_names:
            if gaap_name in us_gaap:
                data = extract_quarterly_data(us_gaap[gaap_name]['units'])
                if data:
                    break
        extracted[key] = data
    
    # 저장
    saved_count = 0
    max_quarters = 20
    
    # OCF 기준으로 분기 결정
    for i, (end_date, ocf_value) in enumerate(extracted['ocf'][:max_quarters]):
        year = int(end_date[:4])
        month = int(end_date[5:7])
        quarter = ((month - 1) // 3) + 1
        
        # 해당 분기 데이터 찾기
        def find_value(data_list, target_date):
            for date, value in data_list:
                if date == target_date:
                    return value
            return None
        
        capex = find_value(extracted['capex'], end_date)
        net_income = find_value(extracted['net_income'], end_date)
        revenue = find_value(extracted['revenue'], end_date)
        assets = find_value(extracted['total_assets'], end_date)
        liabilities = find_value(extracted['total_liabilities'], end_date)
        equity = find_value(extracted['total_equity'], end_date)
        
        # FCF 계산
        fcf = None
        if ocf_value is not None and capex is not None:
            fcf = ocf_value + capex  # CAPEX는 음수
        
        # DB 저장
        StockFinancialRaw.objects.update_or_create(
            stock=stock,
            disclosure_year=year,
            disclosure_quarter=quarter,
            defaults={
                'disclosure_date': end_date,
                'ocf': ocf_value,
                'capex': capex,
                'fcf': fcf,
                'revenue': revenue,
                'net_income': net_income,
                'total_assets': assets,
                'total_liabilities': liabilities,
                'total_equity': equity,
                'data_source': 'EDGAR',
            }
        )
        saved_count += 1
    
    return saved_count


def extract_quarterly_data(units):
    """순수 분기 데이터만 추출"""
    usd_data = units.get('USD', [])
    if not usd_data:
        return []
    
    result = []
    seen_dates = set()
    
    for item in usd_data:
        # 10-Q, 10-K만
        if item.get('form') not in ['10-Q', '10-K']:
            continue
        
        end_date = item.get('end')
        start_date = item.get('start')
        value = item.get('val')
        
        if not end_date or value is None or not start_date:
            continue
        
        if end_date in seen_dates:
            continue
        
        # 분기 데이터 체크 (약 3개월)
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            days = (end - start).days
            
            # 60일 ~ 130일 (약 2-4개월)
            if 60 <= days <= 130:
                result.append((end_date, value))
                seen_dates.add(end_date)
        except:
            continue
    
    # 최신순 정렬
    result.sort(reverse=True)
    return result


def main():
    """메인 실행 함수"""
    print("\n" + "="*60)
    print("🚀 S&P 500 전체 종목 수집 시작")
    print("="*60)
    
    # S&P 500 티커 가져오기
    tickers = get_sp500_tickers()
    
    if not tickers:
        print("❌ 티커 목록을 가져올 수 없습니다")
        return
    
    print(f"\n📊 총 {len(tickers)}개 종목 수집 예정")
    print(f"⏱️  예상 소요 시간: 약 {len(tickers) * 6 // 60}분")
    
    input("\n계속하려면 Enter를 누르세요...")
    
    success_count = 0
    fail_count = 0
    
    for i, ticker in enumerate(tickers, 1):
        print(f"\n[{i}/{len(tickers)}] {ticker} 수집 중...")
        
        # CIK 조회
        cik = get_cik_from_ticker(ticker)
        if not cik:
            print(f"   ❌ CIK를 찾을 수 없음")
            fail_count += 1
            continue
        
        print(f"   CIK: {cik}")
        
        # 데이터 수집
        stock, result_msg = collect_stock_data(ticker, cik)
        
        if stock and "Success" in result_msg:
            print(f"   ✅ {result_msg}")
            success_count += 1
        else:
            print(f"   ❌ {result_msg}")
            fail_count += 1
        
        # Rate limit (10 requests/second)
        time.sleep(0.15)
        
        # 진행 상황 표시
        if i % 10 == 0:
            print(f"\n📊 진행률: {i}/{len(tickers)} ({(i/len(tickers)*100):.1f}%)")
            print(f"   성공: {success_count}개 | 실패: {fail_count}개")
    
    # 최종 결과
    print("\n" + "="*60)
    print("🎉 S&P 500 수집 완료!")
    print("="*60)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print(f"📊 성공률: {(success_count/(success_count+fail_count)*100):.1f}%")
    print("="*60)


if __name__ == '__main__':
    main()

