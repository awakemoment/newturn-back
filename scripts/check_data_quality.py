"""
데이터 품질 체크 스크립트
- EDGAR API로 수집한 데이터의 정확성 검증
- 실제 공시와 DB 데이터 비교
- 누락/오류 데이터 확인
"""

import os
import sys
import django
import requests
from datetime import datetime
import time

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock, StockFinancialRaw

# 테스트할 주요 종목 (다양한 섹터)
TEST_STOCKS = [
    'AAPL',   # 테크
    'MSFT',   # 테크
    'GOOGL',  # 테크
    'NVDA',   # 반도체
    'JPM',    # 금융
    'JNJ',    # 헬스케어
    'XOM',    # 에너지
    'PG',     # 소비재
    'WMT',    # 리테일
    'V',      # 금융서비스
]

def get_edgar_data(ticker):
    """EDGAR API에서 직접 데이터 가져오기"""
    try:
        # CIK 조회
        from sec_cik_mapper import StockMapper
        mapper = StockMapper()
        cik = mapper.ticker_to_cik.get(ticker)
        
        if not cik:
            return None, f"CIK not found for {ticker}"
        
        # CIK를 10자리로 포맷
        cik_str = str(cik).zfill(10)
        
        # EDGAR API 호출
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


def extract_financial_metrics(data):
    """EDGAR 데이터에서 재무 지표 추출"""
    try:
        facts = data.get('facts', {}).get('us-gaap', {})
        
        metrics = {
            'OCF': None,
            'FCF': None,
            'CAPEX': None,
            'NetIncome': None,
            'Revenue': None,
            'Assets': None,
            'Liabilities': None,
            'Equity': None,
        }
        
        # OCF (Operating Cash Flow)
        ocf_key = 'NetCashProvidedByUsedInOperatingActivities'
        if ocf_key in facts:
            units = facts[ocf_key].get('units', {}).get('USD', [])
            if units:
                latest = sorted(units, key=lambda x: x.get('end', ''), reverse=True)[0]
                metrics['OCF'] = latest.get('val')
        
        # CAPEX
        capex_key = 'PaymentsToAcquirePropertyPlantAndEquipment'
        if capex_key in facts:
            units = facts[capex_key].get('units', {}).get('USD', [])
            if units:
                latest = sorted(units, key=lambda x: x.get('end', ''), reverse=True)[0]
                metrics['CAPEX'] = abs(latest.get('val', 0))  # CAPEX는 음수로 나올 수 있음
        
        # FCF = OCF - CAPEX
        if metrics['OCF'] and metrics['CAPEX']:
            metrics['FCF'] = metrics['OCF'] - metrics['CAPEX']
        
        # Net Income
        ni_key = 'NetIncomeLoss'
        if ni_key in facts:
            units = facts[ni_key].get('units', {}).get('USD', [])
            if units:
                latest = sorted(units, key=lambda x: x.get('end', ''), reverse=True)[0]
                metrics['NetIncome'] = latest.get('val')
        
        # Revenue
        rev_key = 'Revenues'
        if rev_key not in facts:
            rev_key = 'RevenueFromContractWithCustomerExcludingAssessedTax'
        if rev_key in facts:
            units = facts[rev_key].get('units', {}).get('USD', [])
            if units:
                latest = sorted(units, key=lambda x: x.get('end', ''), reverse=True)[0]
                metrics['Revenue'] = latest.get('val')
        
        # Assets
        assets_key = 'Assets'
        if assets_key in facts:
            units = facts[assets_key].get('units', {}).get('USD', [])
            if units:
                latest = sorted(units, key=lambda x: x.get('end', ''), reverse=True)[0]
                metrics['Assets'] = latest.get('val')
        
        # Liabilities
        liab_key = 'Liabilities'
        if liab_key in facts:
            units = facts[liab_key].get('units', {}).get('USD', [])
            if units:
                latest = sorted(units, key=lambda x: x.get('end', ''), reverse=True)[0]
                metrics['Liabilities'] = latest.get('val')
        
        # Equity
        equity_key = 'StockholdersEquity'
        if equity_key in facts:
            units = facts[equity_key].get('units', {}).get('USD', [])
            if units:
                latest = sorted(units, key=lambda x: x.get('end', ''), reverse=True)[0]
                metrics['Equity'] = latest.get('val')
        
        return metrics
        
    except Exception as e:
        print(f"  ⚠️ 지표 추출 오류: {e}")
        return None


def check_db_data(ticker):
    """DB에 저장된 데이터 확인"""
    try:
        stock = Stock.objects.get(stock_code=ticker)
        financials = StockFinancialRaw.objects.filter(stock=stock).order_by('-disclosure_date')
        
        if not financials.exists():
            return None, "재무 데이터 없음"
        
        latest = financials.first()
        
        db_metrics = {
            'OCF': latest.ocf,
            'FCF': latest.fcf,
            'CAPEX': latest.capex,
            'NetIncome': latest.net_income,
            'Revenue': latest.revenue,
            'Assets': latest.total_assets,
            'Liabilities': latest.total_liabilities,
            'Equity': latest.total_equity,
            'fiscal_date': latest.disclosure_date,
            'quarters_count': financials.count(),
        }
        
        return db_metrics, None
        
    except Stock.DoesNotExist:
        return None, "종목 없음"
    except Exception as e:
        return None, str(e)


def compare_values(edgar_val, db_val, tolerance=0.01):
    """
    두 값 비교 (허용 오차 1%)
    """
    if edgar_val is None and db_val is None:
        return True, "둘 다 없음"
    
    if edgar_val is None:
        return False, f"EDGAR 없음 (DB: {db_val:,.0f})"
    
    if db_val is None:
        return False, f"DB 없음 (EDGAR: {edgar_val:,.0f})"
    
    # 오차 계산
    diff = abs(edgar_val - db_val)
    avg = (abs(edgar_val) + abs(db_val)) / 2
    
    if avg == 0:
        return edgar_val == db_val, "둘 다 0"
    
    error_rate = diff / avg
    
    if error_rate <= tolerance:
        return True, f"일치 (오차 {error_rate*100:.2f}%)"
    else:
        return False, f"불일치 (오차 {error_rate*100:.2f}%, EDGAR: {edgar_val:,.0f}, DB: {db_val:,.0f})"


def check_stock_quality(ticker):
    """종목 데이터 품질 체크"""
    print(f"\n{'='*60}")
    print(f"📊 {ticker} 데이터 품질 체크")
    print(f"{'='*60}")
    
    # 1. EDGAR 데이터 가져오기
    print(f"  🔍 EDGAR API 조회 중...")
    edgar_data, error = get_edgar_data(ticker)
    
    if error:
        print(f"  ❌ EDGAR 오류: {error}")
        return {
            'ticker': ticker,
            'status': 'EDGAR_ERROR',
            'error': error
        }
    
    edgar_metrics = extract_financial_metrics(edgar_data)
    
    if not edgar_metrics:
        print(f"  ❌ EDGAR 지표 추출 실패")
        return {
            'ticker': ticker,
            'status': 'EXTRACT_ERROR'
        }
    
    print(f"  ✅ EDGAR 데이터 획득")
    
    # 2. DB 데이터 확인
    print(f"  🔍 DB 데이터 조회 중...")
    db_metrics, error = check_db_data(ticker)
    
    if error:
        print(f"  ❌ DB 오류: {error}")
        return {
            'ticker': ticker,
            'status': 'DB_ERROR',
            'error': error,
            'edgar_metrics': edgar_metrics
        }
    
    print(f"  ✅ DB 데이터 획득 (분기 수: {db_metrics['quarters_count']})")
    print(f"  📅 최신 데이터: {db_metrics['fiscal_date']}")
    
    # 3. 비교
    print(f"\n  📈 재무 지표 비교:")
    
    results = {}
    metrics_to_check = ['OCF', 'CAPEX', 'FCF', 'NetIncome', 'Revenue', 'Assets', 'Liabilities', 'Equity']
    
    all_match = True
    for metric in metrics_to_check:
        match, msg = compare_values(edgar_metrics.get(metric), db_metrics.get(metric))
        results[metric] = {
            'match': match,
            'message': msg,
            'edgar': edgar_metrics.get(metric),
            'db': db_metrics.get(metric)
        }
        
        icon = "✅" if match else "⚠️"
        print(f"    {icon} {metric:15s}: {msg}")
        
        if not match:
            all_match = False
    
    # 4. 결과
    if all_match:
        print(f"\n  ✅ 모든 지표 일치! 데이터 품질 우수")
        status = 'PERFECT'
    else:
        print(f"\n  ⚠️ 일부 지표 불일치 - 확인 필요")
        status = 'PARTIAL'
    
    return {
        'ticker': ticker,
        'status': status,
        'edgar_metrics': edgar_metrics,
        'db_metrics': db_metrics,
        'comparison': results
    }


def main():
    print("\n" + "="*60)
    print("🔍 데이터 품질 체크 시작")
    print("="*60)
    print(f"📌 테스트 종목: {len(TEST_STOCKS)}개")
    print(f"📋 종목 리스트: {', '.join(TEST_STOCKS)}")
    print("="*60)
    
    results = []
    
    for i, ticker in enumerate(TEST_STOCKS, 1):
        print(f"\n[{i}/{len(TEST_STOCKS)}] 체크 중...")
        
        result = check_stock_quality(ticker)
        results.append(result)
        
        # API 호출 제한 고려
        if i < len(TEST_STOCKS):
            time.sleep(0.2)
    
    # 최종 요약
    print("\n" + "="*60)
    print("📊 최종 요약")
    print("="*60)
    
    perfect = sum(1 for r in results if r.get('status') == 'PERFECT')
    partial = sum(1 for r in results if r.get('status') == 'PARTIAL')
    edgar_error = sum(1 for r in results if r.get('status') == 'EDGAR_ERROR')
    db_error = sum(1 for r in results if r.get('status') == 'DB_ERROR')
    extract_error = sum(1 for r in results if r.get('status') == 'EXTRACT_ERROR')
    
    print(f"  ✅ 완벽 일치: {perfect}/{len(TEST_STOCKS)}")
    print(f"  ⚠️ 부분 일치: {partial}/{len(TEST_STOCKS)}")
    print(f"  ❌ EDGAR 오류: {edgar_error}/{len(TEST_STOCKS)}")
    print(f"  ❌ DB 오류: {db_error}/{len(TEST_STOCKS)}")
    print(f"  ❌ 추출 오류: {extract_error}/{len(TEST_STOCKS)}")
    
    success_rate = (perfect + partial) / len(TEST_STOCKS) * 100
    print(f"\n  📈 성공률: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print(f"\n  ✅ 결론: 데이터 품질 양호 - 개발 진행 가능")
    elif success_rate >= 50:
        print(f"\n  ⚠️ 결론: 데이터 품질 보통 - 일부 보완 필요")
    else:
        print(f"\n  ❌ 결론: 데이터 품질 불량 - 수집 로직 개선 필요")
    
    # 문제 종목 상세
    problem_stocks = [r for r in results if r.get('status') not in ['PERFECT', 'PARTIAL']]
    if problem_stocks:
        print(f"\n  ⚠️ 문제 종목:")
        for r in problem_stocks:
            print(f"    - {r['ticker']}: {r.get('status')} - {r.get('error', '')}")
    
    print("\n" + "="*60)
    print("✅ 데이터 품질 체크 완료!")
    print("="*60)


if __name__ == '__main__':
    main()

