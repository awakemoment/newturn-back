"""
미국 주식 재무 데이터 수집 (고속 버전)

EDGAR API로 재무제표 데이터를 수집하여 DB에 저장

특징:
- 멀티스레딩: 최대 5개 종목 동시 처리
- 배치 저장: 50개씩 모아서 DB 저장
- 진행 상황: CSV로 저장, 중단 후 재개 가능
- 재시도: 실패 시 3번까지 재시도
- 최근 5년 데이터 수집 (분기별)

수집 항목:
- OCF (영업활동 현금흐름)
- ICF (투자활동 현금흐름)
- CAPEX (설비투자)
- FCF (잉여현금흐름 = OCF - CAPEX)
- 순이익, 총자산, 자본, 부채

사용법:
    python scripts/collect_financial_data.py
    python scripts/collect_financial_data.py --limit 10  # 테스트용 (10개만)
"""

import os
import sys
import django
from datetime import datetime, date
import time
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import argparse

# Django 설정
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from sec_edgar_api import EdgarClient
from apps.stocks.models import Stock, StockFinancialRaw


# 설정
MAX_WORKERS = 5  # 동시 처리 개수
BATCH_SIZE = 50  # DB 배치 저장 크기
RETRY_COUNT = 3  # 재시도 횟수
REQUEST_DELAY = 0.2  # 요청 간 딜레이 (초)
PROGRESS_FILE = 'progress_financial.csv'  # 진행 상황 파일

# 전역 변수
lock = Lock()
progress_data = {
    'success': 0,
    'failed': 0,
    'no_data': 0,
}

# EDGAR 클라이언트 (재사용)
edgar = EdgarClient(user_agent="newturn support@awakemoment.io")


def load_progress():
    """진행 상황 로드"""
    if not os.path.exists(PROGRESS_FILE):
        return set()
    
    processed = set()
    with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('status') in ['success', 'no_data']:
                processed.add(row['stock_code'])
    return processed


def save_progress(stock_code, status, message='', data_count=0):
    """진행 상황 저장"""
    file_exists = os.path.exists(PROGRESS_FILE)
    
    with lock:
        with open(PROGRESS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['stock_code', 'status', 'data_count', 'message', 'timestamp'])
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'stock_code': stock_code,
                'status': status,
                'data_count': data_count,
                'message': message[:100] if message else '',
                'timestamp': datetime.now().isoformat()
            })


def parse_edgar_date(date_str):
    """EDGAR 날짜 파싱 (YYYY-MM-DD)"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return None


def determine_quarter(end_date):
    """날짜로 분기 판단"""
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
    EDGAR units 데이터에서 최신 값 추출
    분기별로 그룹화하고 각 분기의 최신 값만 사용
    """
    if unit not in units_data:
        return []
    
    data_list = units_data[unit]
    
    # 날짜별로 정렬
    sorted_data = sorted(data_list, key=lambda x: x.get('end', ''), reverse=True)
    
    # 최근 5년 데이터만 (20개 분기)
    recent_data = []
    seen_quarters = set()
    
    for item in sorted_data:
        end_date_str = item.get('end')
        if not end_date_str:
            continue
        
        end_date = parse_edgar_date(end_date_str)
        if not end_date:
            continue
        
        year = end_date.year
        quarter = determine_quarter(end_date)
        key = f"{year}Q{quarter}"
        
        # 같은 분기 중복 제거
        if key not in seen_quarters:
            recent_data.append({
                'year': year,
                'quarter': quarter,
                'date': end_date,
                'value': item.get('val'),
            })
            seen_quarters.add(key)
        
        # 최근 20개 분기면 충분
        if len(recent_data) >= 20:
            break
    
    return recent_data


def fetch_financial_data(stock):
    """
    단일 종목의 재무 데이터 조회
    """
    stock_code = stock.stock_code
    cik = stock.corp_code
    
    for attempt in range(RETRY_COUNT):
        try:
            # Rate limiting
            time.sleep(REQUEST_DELAY)
            
            # Company Facts 조회
            facts = edgar.get_company_facts(cik=cik)
            
            if 'facts' not in facts or 'us-gaap' not in facts['facts']:
                return [], f"US-GAAP 데이터 없음"
            
            us_gaap = facts['facts']['us-gaap']
            
            # 수집할 항목 (우선순위 있는 여러 필드명)
            items_map = {
                'ocf': ['NetCashProvidedByUsedInOperatingActivities', 
                        'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations'],
                'icf': ['NetCashProvidedByUsedInInvestingActivities',
                        'NetCashProvidedByUsedInInvestingActivitiesContinuingOperations'],
                'capex': ['PaymentsToAcquirePropertyPlantAndEquipment',
                          'PaymentsToAcquireProductiveAssets'],
                'net_income': ['NetIncomeLoss', 'ProfitLoss'],
                'total_assets': ['Assets'],
                'total_liabilities': ['Liabilities'],
                'total_equity': ['StockholdersEquity',
                                 'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'],
                'revenue': ['SalesRevenueNet', 'SalesRevenueGoodsNet', 'Revenues',
                           'RevenueFromContractWithCustomerExcludingAssessedTax'],
            }
            
            # 각 항목별 데이터 추출 (여러 필드명 시도)
            extracted = {}
            for key, gaap_names in items_map.items():
                # 여러 필드명 시도 (우선순위 순서)
                data = []
                for gaap_name in gaap_names:
                    if gaap_name in us_gaap:
                        data = extract_latest_value(us_gaap[gaap_name]['units'])
                        if data:  # 데이터가 있으면 사용
                            break
                extracted[key] = data
            
            # OCF가 없으면 의미 없음
            if not extracted.get('ocf'):
                return [], "OCF 데이터 없음"
            
            # OCF 기준으로 분기별 데이터 생성
            financials = []
            
            for ocf_item in extracted['ocf']:
                year = ocf_item['year']
                quarter = ocf_item['quarter']
                end_date = ocf_item['date']
                
                # 다른 항목에서 같은 분기 데이터 찾기
                financial_data = {
                    'stock': stock,
                    'disclosure_year': year,
                    'disclosure_quarter': quarter,
                    'disclosure_date': end_date,
                    'ocf': ocf_item['value'],
                    'data_source': 'EDGAR',
                }
                
                # ICF
                icf_match = next((x for x in extracted.get('icf', []) 
                                 if x['year'] == year and x['quarter'] == quarter), None)
                if icf_match:
                    financial_data['icf'] = icf_match['value']
                
                # CAPEX (절대값으로 변환 - EDGAR는 음수로 저장)
                capex_match = next((x for x in extracted.get('capex', []) 
                                   if x['year'] == year and x['quarter'] == quarter), None)
                if capex_match:
                    financial_data['capex'] = abs(capex_match['value'])
                    # FCF 계산
                    financial_data['fcf'] = ocf_item['value'] - abs(capex_match['value'])
                
                # 순이익
                ni_match = next((x for x in extracted.get('net_income', []) 
                                if x['year'] == year and x['quarter'] == quarter), None)
                if ni_match:
                    financial_data['net_income'] = ni_match['value']
                
                # 총자산
                assets_match = next((x for x in extracted.get('total_assets', []) 
                                    if x['year'] == year and x['quarter'] == quarter), None)
                if assets_match:
                    financial_data['total_assets'] = assets_match['value']
                
                # 총부채
                liab_match = next((x for x in extracted.get('total_liabilities', []) 
                                  if x['year'] == year and x['quarter'] == quarter), None)
                if liab_match:
                    financial_data['total_liabilities'] = liab_match['value']
                
                # 자본
                equity_match = next((x for x in extracted.get('total_equity', []) 
                                    if x['year'] == year and x['quarter'] == quarter), None)
                if equity_match:
                    financial_data['total_equity'] = equity_match['value']
                
                # 매출
                rev_match = next((x for x in extracted.get('revenue', []) 
                                 if x['year'] == year and x['quarter'] == quarter), None)
                if rev_match:
                    financial_data['revenue'] = rev_match['value']
                
                financials.append(financial_data)
            
            return financials, None
            
        except Exception as e:
            if attempt < RETRY_COUNT - 1:
                time.sleep(1 * (attempt + 1))
                continue
            else:
                return [], str(e)[:100]
    
    return [], "최대 재시도 횟수 초과"


def process_stocks_batch(stocks_batch, batch_num, total_batches):
    """
    배치 단위로 종목 처리
    """
    print(f"\n📦 배치 {batch_num}/{total_batches} 처리 중 ({len(stocks_batch)}개 종목)...")
    
    financials_to_create = []
    
    # 멀티스레딩으로 데이터 수집
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_stock = {
            executor.submit(fetch_financial_data, stock): stock 
            for stock in stocks_batch
        }
        
        for idx, future in enumerate(as_completed(future_to_stock), 1):
            stock = future_to_stock[future]
            
            try:
                financials, error = future.result()
                
                if financials:
                    financials_to_create.extend(financials)
                    
                    with lock:
                        progress_data['success'] += 1
                    
                    save_progress(stock.stock_code, 'success', f"{len(financials)}개 분기 데이터", len(financials))
                    print(f"  [{idx}/{len(stocks_batch)}] ✅ {stock.stock_code}: {len(financials)}개 분기")
                    
                elif error == "OCF 데이터 없음" or error == "US-GAAP 데이터 없음":
                    with lock:
                        progress_data['no_data'] += 1
                    save_progress(stock.stock_code, 'no_data', error)
                    print(f"  [{idx}/{len(stocks_batch)}] ⚠️  {stock.stock_code}: {error}")
                    
                else:
                    with lock:
                        progress_data['failed'] += 1
                    save_progress(stock.stock_code, 'failed', error)
                    print(f"  [{idx}/{len(stocks_batch)}] ❌ {stock.stock_code}: {error}")
                    
            except Exception as e:
                with lock:
                    progress_data['failed'] += 1
                save_progress(stock.stock_code, 'error', str(e)[:100])
                print(f"  [{idx}/{len(stocks_batch)}] ❌ {stock.stock_code}: {str(e)[:50]}")
    
    # 배치 DB 저장
    if financials_to_create:
        print(f"💾 배치 DB 저장 중 ({len(financials_to_create)}개 분기 데이터)...")
        try:
            # 기존 데이터 삭제 후 재저장 (update_or_create 대신)
            for financial_data in financials_to_create:
                StockFinancialRaw.objects.update_or_create(
                    stock=financial_data['stock'],
                    disclosure_year=financial_data['disclosure_year'],
                    disclosure_quarter=financial_data['disclosure_quarter'],
                    defaults=financial_data
                )
            print(f"  ✅ 저장 완료: {len(financials_to_create)}개")
        except Exception as e:
            print(f"  ❌ DB 저장 에러: {e}")


def collect_financial_data(limit=None):
    """
    미국 주식 재무 데이터 수집
    """
    print("=" * 60)
    print("📊 미국 주식 재무 데이터 수집 (EDGAR API)")
    print("=" * 60)
    print(f"⚙️  설정: 동시처리={MAX_WORKERS}, 배치={BATCH_SIZE}, 딜레이={REQUEST_DELAY}초")
    print("=" * 60)
    print()
    
    # 1. 진행 상황 로드
    print("📂 진행 상황 확인 중...")
    processed_codes = load_progress()
    if processed_codes:
        print(f"✅ 이미 처리된 종목: {len(processed_codes)}개 (건너뛰기)")
    else:
        print("✅ 새로운 작업 시작")
    print()
    
    # 2. 처리할 종목 조회
    print("🔍 DB에서 미국 종목 조회 중...")
    stocks = Stock.objects.filter(
        country='us',
        is_active=True
    ).exclude(
        stock_code__in=processed_codes
    ).order_by('stock_code')
    
    if limit:
        stocks = stocks[:limit]
        print(f"⚠️  테스트 모드: {limit}개만 처리")
    
    total_stocks = stocks.count()
    print(f"✅ 처리할 종목: {total_stocks}개")
    print()
    
    if total_stocks == 0:
        print("✅ 모든 종목이 이미 처리되었습니다!")
        return
    
    # 3. 배치 단위로 처리
    print("=" * 60)
    print("🚀 재무 데이터 수집 시작!")
    print("=" * 60)
    
    start_time = time.time()
    
    # 배치로 나누기
    stocks_list = list(stocks)
    batches = [stocks_list[i:i + BATCH_SIZE] for i in range(0, len(stocks_list), BATCH_SIZE)]
    total_batches = len(batches)
    
    for batch_num, batch in enumerate(batches, 1):
        process_stocks_batch(batch, batch_num, total_batches)
    
    elapsed_time = time.time() - start_time
    
    # 4. 최종 통계
    print()
    print("=" * 60)
    print("📊 수집 완료!")
    print("=" * 60)
    print(f"✅ 성공: {progress_data['success']}개")
    print(f"⚠️  데이터 없음: {progress_data['no_data']}개")
    print(f"❌ 실패: {progress_data['failed']}개")
    print(f"⏱️  소요 시간: {elapsed_time/60:.1f}분")
    if progress_data['success'] > 0:
        print(f"⚡ 평균 속도: {progress_data['success']/(elapsed_time/60):.1f}개/분")
    print()
    
    # DB 통계
    total_financials = StockFinancialRaw.objects.filter(data_source='EDGAR').count()
    total_stocks_with_data = StockFinancialRaw.objects.filter(
        data_source='EDGAR'
    ).values('stock').distinct().count()
    
    print(f"💾 DB 통계:")
    print(f"  - 재무 데이터: {total_financials}개 (분기별)")
    print(f"  - 데이터 있는 종목: {total_stocks_with_data}개")
    print()
    print(f"📂 진행 상황 파일: {PROGRESS_FILE}")
    print("   → 중단 후 다시 실행하면 이어서 진행됩니다!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='미국 주식 재무 데이터 수집')
    parser.add_argument('--limit', type=int, help='처리할 종목 수 제한 (테스트용)')
    args = parser.parse_args()
    
    collect_financial_data(limit=args.limit)

