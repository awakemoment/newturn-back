"""
EDGAR 데이터가 없는 종목들에 대해 재무 데이터 수집
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

# EDGAR API 설정
EDGAR_BASE_URL = "https://data.sec.gov"
HEADERS = {
    'User-Agent': 'NewTurn Investment Platform admin@newturn.com',
    'Accept-Encoding': 'gzip, deflate',
}


def get_company_facts(cik):
    """회사 재무 데이터 가져오기"""
    if not cik:
        return None
    
    # CIK는 10자리 숫자여야 함
    cik_padded = str(cik).zfill(10)
    url = f"{EDGAR_BASE_URL}/api/xbrl/companyfacts/CIK{cik_padded}.json"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None  # CIK 없음
        raise
    except Exception as e:
        return None


def extract_quarterly_data(facts_data, stock):
    """분기별 재무 데이터 추출 및 저장 (10-Q만)"""
    if not facts_data or 'facts' not in facts_data:
        return 0
    
    saved_count = 0
    facts = facts_data.get('facts', {})
    
    # US-GAAP 데이터만 처리 (IFRS는 제외)
    us_gaap = facts.get('us-gaap', {})
    
    if not us_gaap:
        # US-GAAP 데이터 없으면 외국 기업일 가능성
        return 0
    
    # 필요한 재무 항목
    revenue_data = us_gaap.get('Revenues', {}).get('units', {}).get('USD', [])
    if not revenue_data:
        revenue_data = us_gaap.get('SalesRevenueNet', {}).get('units', {}).get('USD', [])
    
    ocf_data = us_gaap.get('NetCashProvidedByUsedInOperatingActivities', {}).get('units', {}).get('USD', [])
    capex_data = us_gaap.get('PaymentsToAcquirePropertyPlantAndEquipment', {}).get('units', {}).get('USD', [])
    net_income_data = us_gaap.get('NetIncomeLoss', {}).get('units', {}).get('USD', [])
    
    # 분기별 데이터만 필터링 (10-Q)
    quarterly_data = {}
    
    for item in revenue_data:
        if item.get('form') == '10-Q' and item.get('fp') in ['Q1', 'Q2', 'Q3', 'Q4']:
            key = f"{item['fy']}-{item['fp']}"
            if key not in quarterly_data:
                quarterly_data[key] = {
                    'fiscal_year': item['fy'],
                    'quarter': item['fp'],
                    'filed': item.get('filed'),
                }
            quarterly_data[key]['revenue'] = item.get('val')
    
    # OCF 추가
    for item in ocf_data:
        if item.get('form') == '10-Q' and item.get('fp') in ['Q1', 'Q2', 'Q3', 'Q4']:
            key = f"{item['fy']}-{item['fp']}"
            if key in quarterly_data:
                quarterly_data[key]['ocf'] = item.get('val')
    
    # CAPEX 추가 (음수로 저장됨)
    for item in capex_data:
        if item.get('form') == '10-Q' and item.get('fp') in ['Q1', 'Q2', 'Q3', 'Q4']:
            key = f"{item['fy']}-{item['fp']}"
            if key in quarterly_data:
                capex = item.get('val')
                quarterly_data[key]['capex'] = abs(capex) if capex else None
    
    # Net Income 추가
    for item in net_income_data:
        if item.get('form') == '10-Q' and item.get('fp') in ['Q1', 'Q2', 'Q3', 'Q4']:
            key = f"{item['fy']}-{item['fp']}"
            if key in quarterly_data:
                quarterly_data[key]['net_income'] = item.get('val')
    
    # DB 저장
    for key, data in quarterly_data.items():
        if not data.get('revenue'):
            continue
        
        quarter_map = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}
        quarter_num = quarter_map.get(data['quarter'], 1)
        
        ocf = data.get('ocf')
        capex = data.get('capex')
        fcf = (ocf - capex) if (ocf is not None and capex is not None) else None
        
        try:
            # filed 날짜를 disclosure_date로 변환
            from datetime import datetime
            filed_str = data.get('filed')
            if filed_str:
                disclosure_date = datetime.strptime(filed_str, '%Y-%m-%d').date()
            else:
                # filed 정보 없으면 회계연도 마지막 날로 추정
                disclosure_date = datetime(data['fiscal_year'], quarter_num * 3, 1).date()
            
            StockFinancialRaw.objects.update_or_create(
                stock=stock,
                disclosure_year=data['fiscal_year'],
                disclosure_quarter=quarter_num,
                data_source='EDGAR',
                defaults={
                    'revenue': data.get('revenue'),
                    'ocf': ocf,
                    'capex': capex,
                    'fcf': fcf,
                    'net_income': data.get('net_income'),
                    'disclosure_date': disclosure_date,
                }
            )
            saved_count += 1
        except Exception as e:
            print(f"      ⚠️ 저장 실패: {e}")
            continue
    
    return saved_count


def main():
    print("\n" + "="*70)
    print("📊 EDGAR 누락 데이터 수집")
    print("="*70)
    
    # EDGAR 데이터가 없는 종목 찾기
    stocks_with_edgar = Stock.objects.filter(
        financials_raw__data_source='EDGAR'
    ).distinct().values_list('id', flat=True)
    
    # 미국 기업만 (외국 기업 제외)
    # 외국 기업 식별: PLC, SE, SA, NV, AB, ASA, Oyj 등
    foreign_keywords = ['PLC', 'SE', 'SA', 'NV', 'AB', 'ASA', 'Oyj', 'SpA', 'AG', 'Ltd.']
    
    missing_stocks = Stock.objects.filter(
        country='us'
    ).exclude(
        id__in=stocks_with_edgar
    )
    
    # 외국 기업 필터링 (더 정확하게)
    for keyword in foreign_keywords:
        missing_stocks = missing_stocks.exclude(stock_name__icontains=keyword)
    
    # ADR (American Depositary Receipt) 제외
    missing_stocks = missing_stocks.exclude(stock_name__icontains='ADR')
    if missing_stocks.model._meta.get_field('description'):
        missing_stocks = missing_stocks.exclude(description__icontains='ADR')
    
    # 이미 EDGAR 데이터가 있는 종목 중 US-GAAP이 있는 종목만 (성공 사례 학습)
    # → 너무 복잡하니 일단 스킵하고, US-GAAP 없으면 자동으로 스킵됨
    
    total = missing_stocks.count()
    print(f"\n📌 EDGAR 데이터 누락 종목: {total:,}개 (미국 기업만)")
    print(f"   외국 기업은 제외됨 (20-F 사용)")
    
    # CIK 없는 종목 체크
    missing_cik_count = missing_stocks.filter(corp_code__isnull=True).count()
    missing_cik_count += missing_stocks.filter(corp_code='').count()
    
    if missing_cik_count > 0:
        print(f"⚠️  CIK 없는 종목: {missing_cik_count:,}개")
        print(f"   → download_ticker_cik_mapping.py 먼저 실행 필요!")
    
    actual_to_collect = total - missing_cik_count
    print(f"⏱️  실제 수집 대상: {actual_to_collect:,}개")
    print(f"⏱️  예상 소요 시간: ~{actual_to_collect // 10}분 (API Rate Limit: 10 calls/sec)")
    print()
    
    success_count = 0
    fail_count = 0
    
    for i, stock in enumerate(missing_stocks, 1):
        print(f"[{i}/{total}] {stock.stock_code} - {stock.stock_name[:30]}")
        
        # CIK 확인 (corp_code에 저장되어 있어야 함)
        if not stock.corp_code:
            print(f"   ⚠️ CIK 없음 (매핑 필요)")
            fail_count += 1
            continue
        
        facts = get_company_facts(stock.corp_code)
        
        if facts:
            saved = extract_quarterly_data(facts, stock)
            if saved > 0:
                print(f"   ✅ {saved}개 분기 데이터 저장")
                success_count += 1
            else:
                print(f"   ⚠️ 데이터 없음")
                fail_count += 1
        else:
            print(f"   ❌ API 호출 실패")
            fail_count += 1
        
        # Rate Limit 준수
        time.sleep(0.11)  # 초당 10회 제한
        
        # 진행 상황
        if i % 50 == 0:
            print(f"\n📊 진행률: {i}/{total} ({i/total*100:.1f}%)")
            print(f"   성공: {success_count}개 | 실패: {fail_count}개\n")
    
    # 최종 결과
    print("\n" + "="*70)
    print("🎉 수집 완료!")
    print("="*70)
    print(f"✅ 성공: {success_count:,}개")
    print(f"❌ 실패: {fail_count:,}개")
    print(f"📊 성공률: {success_count/(success_count+fail_count)*100:.1f}%")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()

