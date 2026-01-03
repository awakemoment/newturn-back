"""
S&P 500 + 주요 미국 주식 종목 수집 및 DB 저장 (고속 버전)

멀티스레딩 + 배치 저장 + 진행 상황 저장으로 최적화된 버전

특징:
- 멀티스레딩: 최대 5개 종목 동시 처리 (안전)
- 배치 저장: 100개씩 모아서 DB 저장
- 진행 상황: CSV로 저장, 중단 후 재개 가능
- 재시도: 실패 시 3번까지 재시도
- Rate Limit: SEC API 안전 준수

사용법:
    python scripts/collect_sp500_stocks.py
"""

import os
import sys
import django
from datetime import datetime
import time
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Django 설정
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

# Wikipedia 403 에러 방지 - User-Agent 설정
import urllib.request
opener = urllib.request.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')]
urllib.request.install_opener(opener)

import FinanceDataReader as fdr
from sec_edgar_api import EdgarClient
from sec_cik_mapper import StockMapper

from apps.stocks.models import Stock


# 설정
MAX_WORKERS = 5  # 동시 처리 개수 (SEC API 안전)
BATCH_SIZE = 100  # DB 배치 저장 크기
RETRY_COUNT = 3  # 재시도 횟수
REQUEST_DELAY = 0.15  # 요청 간 딜레이 (초)
PROGRESS_FILE = 'progress_stocks.csv'  # 진행 상황 파일

# 전역 변수
lock = Lock()
progress_data = {
    'processed': [],
    'success': 0,
    'failed': 0,
    'skipped': 0,
}


def load_progress():
    """진행 상황 로드"""
    if not os.path.exists(PROGRESS_FILE):
        return set()
    
    processed = set()
    with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('status') == 'success':
                processed.add(row['stock_code'])
    return processed


def save_progress(stock_code, status, message=''):
    """진행 상황 저장"""
    file_exists = os.path.exists(PROGRESS_FILE)
    
    with lock:
        with open(PROGRESS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['stock_code', 'status', 'message', 'timestamp'])
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'stock_code': stock_code,
                'status': status,
                'message': message[:100] if message else '',
                'timestamp': datetime.now().isoformat()
            })


def fetch_stock_info(stock_code, ticker_to_cik, edgar, df_NASDAQ, df_SP500, df_NYSE, df_AMEX):
    """
    단일 종목 정보 조회 (재시도 포함)
    """
    for attempt in range(RETRY_COUNT):
        try:
            # Rate limiting
            time.sleep(REQUEST_DELAY)
            
            # EDGAR API로 기업 정보 조회
            cik_code = ticker_to_cik[stock_code]
            stock_info = edgar.get_submissions(cik=cik_code)
            
            if not stock_info.get('fiscalYearEnd'):
                return None, f"회계연도 정보 없음"
            
            # 회계연도 처리
            if stock_info['fiscalYearEnd'] == '0229':
                fiscal_year_end = '0228'
            else:
                fiscal_year_end = stock_info['fiscalYearEnd']
            
            fiscal_time = datetime.strptime(fiscal_year_end, '%m%d')
            fiscal_month = fiscal_time.strftime('%m')
            
            # 거래소 정보
            if not stock_info.get('exchanges'):
                if df_SP500 is not None and stock_code in list(df_SP500['Symbol']):
                    exchange = 'sp500'
                elif df_NASDAQ is not None and stock_code in list(df_NASDAQ['Symbol']):
                    exchange = 'nasdaq'
                elif df_NYSE is not None and stock_code in list(df_NYSE['Symbol']):
                    exchange = 'nyse'
                elif df_AMEX is not None and stock_code in list(df_AMEX['Symbol']):
                    exchange = 'amex'
                else:
                    exchange = 'nasdaq'
            else:
                exchange = stock_info['exchanges'][0]
            
            # Stock 객체 생성 (아직 저장 안 함)
            stock_data = {
                'stock_code': stock_code,
                'stock_name': stock_info['name'],
                'stock_name_en': stock_info['name'],
                'corp_code': cik_code,
                'country': 'us',
                'exchange': exchange.lower() if exchange else 'nasdaq',
                'sector': stock_info.get('category', ''),
            }
            
            return stock_data, None
            
        except Exception as e:
            if attempt < RETRY_COUNT - 1:
                time.sleep(1 * (attempt + 1))  # 백오프
                continue
            else:
                return None, str(e)[:100]
    
    return None, "최대 재시도 횟수 초과"


def process_stocks_batch(stock_codes_batch, ticker_to_cik, edgar, df_NASDAQ, df_SP500, df_NYSE, df_AMEX, batch_num, total_batches):
    """
    배치 단위로 종목 처리
    """
    print(f"\n📦 배치 {batch_num}/{total_batches} 처리 중 ({len(stock_codes_batch)}개 종목)...")
    
    stocks_to_create = []
    stocks_to_update = []
    
    # 멀티스레딩으로 데이터 수집
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_code = {
            executor.submit(
                fetch_stock_info, 
                code, 
                ticker_to_cik, 
                edgar,
                df_NASDAQ,
                df_SP500,
                df_NYSE,
                df_AMEX
            ): code 
            for code in stock_codes_batch
        }
        
        for idx, future in enumerate(as_completed(future_to_code), 1):
            stock_code = future_to_code[future]
            
            try:
                stock_data, error = future.result()
                
                if stock_data:
                    # DB에 이미 있는지 확인
                    try:
                        existing = Stock.objects.get(stock_code=stock_code)
                        # 업데이트
                        for key, value in stock_data.items():
                            setattr(existing, key, value)
                        stocks_to_update.append(existing)
                        status = '🔄'
                    except Stock.DoesNotExist:
                        # 새로 생성
                        stocks_to_create.append(Stock(**stock_data))
                        status = '✅'
                    
                    with lock:
                        progress_data['success'] += 1
                    
                    save_progress(stock_code, 'success', stock_data['stock_name'])
                    print(f"  [{idx}/{len(stock_codes_batch)}] {status} {stock_code}: {stock_data['stock_name'][:40]}")
                else:
                    with lock:
                        progress_data['failed'] += 1
                    save_progress(stock_code, 'failed', error)
                    print(f"  [{idx}/{len(stock_codes_batch)}] ❌ {stock_code}: {error}")
                    
            except Exception as e:
                with lock:
                    progress_data['failed'] += 1
                save_progress(stock_code, 'error', str(e)[:100])
                print(f"  [{idx}/{len(stock_codes_batch)}] ❌ {stock_code}: {str(e)[:50]}")
    
    # 배치 DB 저장
    print(f"💾 배치 DB 저장 중...")
    try:
        if stocks_to_create:
            Stock.objects.bulk_create(stocks_to_create, ignore_conflicts=True)
            print(f"  ✅ 신규 저장: {len(stocks_to_create)}개")
        
        if stocks_to_update:
            Stock.objects.bulk_update(
                stocks_to_update, 
                ['stock_name', 'stock_name_en', 'corp_code', 'country', 'exchange', 'sector']
            )
            print(f"  ✅ 업데이트: {len(stocks_to_update)}개")
    except Exception as e:
        print(f"  ❌ DB 저장 에러: {e}")


def collect_us_stocks():
    """
    미국 주식 종목 리스트 수집 (고속 버전)
    """
    print("=" * 60)
    print("📊 미국 주식 종목 리스트 수집 (고속 멀티스레딩)")
    print("=" * 60)
    print(f"⚙️  설정: 동시처리={MAX_WORKERS}, 배치={BATCH_SIZE}, 딜레이={REQUEST_DELAY}초")
    print("=" * 60)
    print()
    
    # 1. 초기화
    print("🔧 초기화 중...")
    mapper = StockMapper()
    edgar = EdgarClient(user_agent="newturn support@awakemoment.io")
    ticker_to_cik = mapper.ticker_to_cik
    print("✅ 초기화 완료")
    print()
    
    # 2. 진행 상황 로드
    print("📂 진행 상황 확인 중...")
    processed_codes = load_progress()
    if processed_codes:
        print(f"✅ 이미 처리된 종목: {len(processed_codes)}개 (건너뛰기)")
    else:
        print("✅ 새로운 작업 시작")
    print()
    
    # 3. 종목 리스트 다운로드
    print("📥 FinanceDataReader로 종목 리스트 다운로드 중...")
    print()
    
    df_NASDAQ = None
    df_SP500 = None
    df_NYSE = None
    df_AMEX = None
    
    try:
        print("  → NASDAQ 다운로드 중...")
        df_NASDAQ = fdr.StockListing('NASDAQ')
        print(f"  ✅ NASDAQ: {len(df_NASDAQ)}개")
    except Exception as e:
        print(f"  ❌ NASDAQ 에러: {e}")
    
    try:
        print("  → S&P 500 다운로드 중...")
        df_SP500 = fdr.StockListing('SP500')
        print(f"  ✅ S&P 500: {len(df_SP500)}개")
    except Exception as e:
        print(f"  ❌ S&P 500 에러: {e}")
    
    try:
        print("  → NYSE 다운로드 중...")
        df_NYSE = fdr.StockListing('NYSE')
        print(f"  ✅ NYSE: {len(df_NYSE)}개")
    except Exception as e:
        print(f"  ❌ NYSE 에러: {e}")
    
    try:
        print("  → AMEX 다운로드 중...")
        df_AMEX = fdr.StockListing('AMEX')
        print(f"  ✅ AMEX: {len(df_AMEX)}개")
    except Exception as e:
        print(f"  ❌ AMEX 에러: {e}")
    
    print()
    
    if df_NASDAQ is None and df_SP500 is None and df_NYSE is None and df_AMEX is None:
        print("❌ 모든 거래소 다운로드 실패")
        return
    
    # 4. CIK 매핑 가능한 종목만 필터링
    print("🔍 CIK 매핑 확인 중...")
    all_symbols = []
    if df_SP500 is not None:
        all_symbols += list(df_SP500['Symbol'])
    if df_NASDAQ is not None:
        all_symbols += list(df_NASDAQ['Symbol'])
    if df_NYSE is not None:
        all_symbols += list(df_NYSE['Symbol'])
    if df_AMEX is not None:
        all_symbols += list(df_AMEX['Symbol'])
    
    stock_codes = [
        stock_name
        for stock_name in all_symbols
        if stock_name in ticker_to_cik.keys()
    ]
    print(f"✅ CIK 매핑 가능: {len(stock_codes)}개")
    print()
    
    # 5. 이미 처리된 종목 제외
    for_save_codes = [code for code in stock_codes if code not in processed_codes]
    
    if len(for_save_codes) == 0:
        print("✅ 모든 종목이 이미 처리되었습니다!")
        print()
        total_in_db = Stock.objects.filter(country='us').count()
        print(f"💾 DB 저장 완료: 총 {total_in_db}개 미국 종목")
        return
    
    print(f"📝 처리할 종목: {len(for_save_codes)}개")
    print(f"⏭️  건너뛴 종목: {len(processed_codes)}개")
    print()
    
    # 6. 배치 단위로 처리
    print("=" * 60)
    print("🚀 고속 수집 시작!")
    print("=" * 60)
    
    start_time = time.time()
    
    # 배치로 나누기
    batches = [for_save_codes[i:i + BATCH_SIZE] for i in range(0, len(for_save_codes), BATCH_SIZE)]
    total_batches = len(batches)
    
    for batch_num, batch in enumerate(batches, 1):
        process_stocks_batch(
            batch, 
            ticker_to_cik, 
            edgar,
            df_NASDAQ,
            df_SP500,
            df_NYSE,
            df_AMEX,
            batch_num,
            total_batches
        )
    
    elapsed_time = time.time() - start_time
    
    # 7. 최종 통계
    print()
    print("=" * 60)
    print("📊 수집 완료!")
    print("=" * 60)
    print(f"✅ 성공: {progress_data['success']}개")
    print(f"❌ 실패: {progress_data['failed']}개")
    print(f"⏱️  소요 시간: {elapsed_time/60:.1f}분")
    print(f"⚡ 평균 속도: {progress_data['success']/(elapsed_time/60):.1f}개/분")
    print()
    
    total_in_db = Stock.objects.filter(country='us').count()
    print(f"💾 DB 저장 완료: 총 {total_in_db}개 미국 종목")
    print()
    print(f"📂 진행 상황 파일: {PROGRESS_FILE}")
    print("   → 중단 후 다시 실행하면 이어서 진행됩니다!")


if __name__ == "__main__":
    collect_us_stocks()
