"""
EDGAR에서 발행주식수(Shares Outstanding) 수집

CommonStockSharesOutstanding 데이터를 수집하여
밸류에이션 정확도를 높입니다.
"""
import os
import sys
import django
import requests
import time
from datetime import date

# Django 설정
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock

# SEC API Headers
HEADERS = {
    'User-Agent': 'Newturn newturn@example.com',
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'data.sec.gov'
}


def pad_cik(cik):
    """CIK를 10자리로 패딩"""
    if cik:
        return str(cik).zfill(10)
    return None


def get_shares_outstanding_from_edgar(cik):
    """
    EDGAR Company Facts API에서 발행주식수 가져오기
    
    Args:
        cik: CIK 번호 (문자열 또는 숫자)
    
    Returns:
        tuple: (shares_outstanding, date) 또는 (None, None)
    """
    padded_cik = pad_cik(cik)
    if not padded_cik:
        return None, None
    
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{padded_cik}.json"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            print(f"  ❌ CIK {padded_cik}: HTTP {response.status_code}")
            return None, None
        
        data = response.json()
        
        # CommonStockSharesOutstanding 찾기
        facts = data.get('facts', {})
        us_gaap = facts.get('us-gaap', {})
        
        if 'CommonStockSharesOutstanding' not in us_gaap:
            print(f"  ⚠️ CIK {padded_cik}: CommonStockSharesOutstanding 없음")
            return None, None
        
        stock_data = us_gaap['CommonStockSharesOutstanding']
        units = stock_data.get('units', {})
        
        # 'shares' 단위 데이터 가져오기
        if 'shares' not in units:
            print(f"  ⚠️ CIK {padded_cik}: shares 단위 없음")
            return None, None
        
        shares_list = units['shares']
        
        # 가장 최근 데이터 찾기 (filed 날짜 기준)
        shares_list_sorted = sorted(
            shares_list,
            key=lambda x: x.get('filed', ''),
            reverse=True
        )
        
        if not shares_list_sorted:
            return None, None
        
        latest = shares_list_sorted[0]
        shares = latest.get('val')
        filed_date = latest.get('filed')  # YYYY-MM-DD 형식
        
        if shares and filed_date:
            # 날짜 파싱
            year, month, day = filed_date.split('-')
            date_obj = date(int(year), int(month), int(day))
            
            print(f"  ✅ {shares:,} shares ({filed_date})")
            return shares, date_obj
        
        return None, None
        
    except requests.exceptions.RequestException as e:
        print(f"  ❌ CIK {padded_cik}: 네트워크 오류 - {e}")
        return None, None
    except Exception as e:
        print(f"  ❌ CIK {padded_cik}: 오류 - {e}")
        return None, None


def load_cik_mapping():
    """ticker-cik 매핑 로드"""
    mapping_file = os.path.join(
        os.path.dirname(__file__),
        '../data/ticker_cik_mapping.txt'
    )
    
    if not os.path.exists(mapping_file):
        print("❌ ticker_cik_mapping.txt 파일이 없습니다!")
        print("먼저 download_ticker_cik_mapping.py를 실행하세요.")
        return {}
    
    mapping = {}
    with open(mapping_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                ticker = parts[0]
                cik = parts[1]
                mapping[ticker] = cik
    
    print(f"✅ {len(mapping):,}개 ticker-CIK 매핑 로드")
    return mapping


def main(limit=None):
    print("=" * 80)
    print("📊 발행주식수 수집")
    print("=" * 80)
    
    # CIK 매핑 로드
    cik_mapping = load_cik_mapping()
    if not cik_mapping:
        return
    
    # 미국 주식 중 shares_outstanding이 없는 종목
    stocks = Stock.objects.filter(
        country='us',
        shares_outstanding__isnull=True
    ).order_by('stock_code')
    
    total = stocks.count()
    print(f"\n📍 대상 종목: {total:,}개")
    
    if limit:
        stocks = stocks[:limit]
        print(f"   (제한: {limit}개만 수집)")
    
    # 통계
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    for idx, stock in enumerate(stocks, 1):
        ticker = stock.stock_code
        
        print(f"\n[{idx}/{len(stocks)}] {ticker} - {stock.stock_name}")
        
        # CIK 찾기
        cik = cik_mapping.get(ticker)
        if not cik:
            print(f"  ⚠️ CIK 매핑 없음")
            skip_count += 1
            continue
        
        # CIK 저장
        stock.cik = cik
        
        # 발행주식수 가져오기
        shares, filed_date = get_shares_outstanding_from_edgar(cik)
        
        if shares:
            stock.shares_outstanding = shares
            stock.shares_outstanding_updated_at = filed_date
            stock.save()
            success_count += 1
        else:
            fail_count += 1
        
        # Rate Limiting (SEC: 10 requests per second)
        time.sleep(0.11)
        
        # 중간 결과 (매 50개마다)
        if idx % 50 == 0:
            print(f"\n📊 중간 결과:")
            print(f"   ✅ 성공: {success_count}")
            print(f"   ❌ 실패: {fail_count}")
            print(f"   ⚠️ 스킵: {skip_count}")
    
    # 최종 결과
    print("\n" + "=" * 80)
    print("📊 최종 결과")
    print("=" * 80)
    print(f"✅ 성공: {success_count:,}개")
    print(f"❌ 실패: {fail_count:,}개")
    print(f"⚠️ 스킵: {skip_count:,}개")
    print(f"📍 성공률: {success_count / (success_count + fail_count) * 100:.1f}%" if (success_count + fail_count) > 0 else "N/A")
    
    # 현재 상태
    total_with_shares = Stock.objects.filter(
        country='us',
        shares_outstanding__isnull=False
    ).count()
    total_us = Stock.objects.filter(country='us').count()
    
    print(f"\n📈 전체 현황:")
    print(f"   발행주식수 보유: {total_with_shares:,}/{total_us:,} ({total_with_shares/total_us*100:.1f}%)")
    print("=" * 80)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='발행주식수 수집')
    parser.add_argument('--limit', type=int, help='수집할 종목 수 제한 (테스트용)')
    
    args = parser.parse_args()
    
    main(limit=args.limit)

