"""
10개 미국 주식 테스트 (EDGAR 전용)

목표: 다양한 섹터/규모의 종목으로 데이터 품질 검증

테스트 종목:
- Tech: AAPL, MSFT, GOOGL, NVDA
- Finance: JPM, BAC
- Consumer: WMT, KO
- Healthcare: JNJ, PFE
"""

from sec_edgar_api import EdgarClient
from sec_cik_mapper import StockMapper
import time


TEST_STOCKS = [
    'AAPL',   # Apple
    'MSFT',   # Microsoft
    'GOOGL',  # Alphabet
    'NVDA',   # Nvidia
    'JPM',    # JPMorgan
    'BAC',    # Bank of America
    'WMT',    # Walmart
    'KO',     # Coca-Cola
    'JNJ',    # Johnson & Johnson
    'PFE',    # Pfizer
]


def test_stock(ticker):
    """개별 종목 테스트 (EDGAR 전용)"""
    print(f"\n{'='*60}")
    print(f"테스트: {ticker}")
    print(f"{'='*60}")
    
    result = {
        'ticker': ticker,
        'edgar_ok': False,
        'cashflow_ok': False,
        'company_name': None,
    }
    
    try:
        # EDGAR
        mapper = StockMapper()
        cik = mapper.ticker_to_cik.get(ticker)
        
        if not cik:
            print(f"❌ CIK를 찾을 수 없습니다")
            return result
        
        result['edgar_ok'] = True
        print(f"✅ EDGAR CIK: {cik}")
        
        # EDGAR 클라이언트
        edgar = EdgarClient(user_agent="Newturn support@newturn.com")
        
        # 기업 정보
        submissions = edgar.get_submissions(cik=cik)
        result['company_name'] = submissions['name']
        print(f"✅ 기업명: {submissions['name']}")
        
        # Company Facts
        facts = edgar.get_company_facts(cik=cik)
        us_gaap = facts['facts']['us-gaap']
        
        # 현금흐름 항목 확인
        ocf_key = 'NetCashProvidedByUsedInOperatingActivities'
        if ocf_key in us_gaap:
            result['cashflow_ok'] = True
            print(f"✅ 현금흐름 데이터: 있음")
        else:
            print(f"⚠️  현금흐름 데이터: 없음")
        
        # Rate Limit 방지
        time.sleep(0.12)  # SEC: 10 req/sec
        
    except Exception as e:
        print(f"❌ 에러: {e}")
    
    return result


if __name__ == "__main__":
    print("="*60)
    print("🧪 10개 미국 주식 데이터 품질 테스트")
    print("="*60)
    
    results = []
    
    for ticker in TEST_STOCKS:
        result = test_stock(ticker)
        results.append(result)
    
    # 종합 결과
    print(f"\n{'='*60}")
    print("📊 종합 결과")
    print(f"{'='*60}\n")
    
    edgar_success = sum(1 for r in results if r['edgar_ok'])
    cf_success = sum(1 for r in results if r['cashflow_ok'])
    
    print(f"EDGAR 연동 성공: {edgar_success}/{len(results)} ({edgar_success/len(results)*100:.0f}%)")
    print(f"현금흐름 데이터: {cf_success}/{len(results)} ({cf_success/len(results)*100:.0f}%)")
    
    if edgar_success >= 8 and cf_success >= 8:  # 80% 이상
        print(f"\n✅ 결론: EDGAR API만으로 충분!")
        print(f"   → OCF/FCF 데이터 {cf_success}/{len(results)}개 제공")
        print(f"   → 무료, 안정적")
        print(f"   → yfinance 불필요")
    else:
        print(f"\n⚠️  결론: 일부 종목 데이터 누락")
        print(f"   → GPT-4 보완 고려")

