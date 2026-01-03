"""
POC: 미국 주식 데이터 수집 (EDGAR 전용)

목표: 
1. EDGAR에서 재무 데이터 (OCF/FCF) 추출
2. EDGAR에서 기업 정보 추출
3. 데이터 품질 검증

테스트 종목: Apple (AAPL)
"""

from sec_edgar_api import EdgarClient
from sec_cik_mapper import StockMapper
from datetime import datetime, timedelta
import json


def test_edgar_basic_info(ticker='AAPL'):
    """
    Step 1: EDGAR로 기업 기본 정보
    """
    print("\n" + "="*60)
    print(f"Step 1: EDGAR 기본 정보 - {ticker}")
    print("="*60)
    
    try:
        stock = yf.Ticker(ticker)
        
        # 기본 정보
        info = stock.info
        print(f"✅ 기업명: {info.get('longName', 'N/A')}")
        print(f"✅ 섹터: {info.get('sector', 'N/A')}")
        print(f"✅ 산업: {info.get('industry', 'N/A')}")
        print(f"✅ 시가총액: ${info.get('marketCap', 0):,}")
        
        # 주가 데이터 (최근 30일)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        hist = stock.history(
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d')
        )
        
        print(f"\n✅ 주가 데이터: {len(hist)}일")
        print(f"최근 가격: ${hist['Close'].iloc[-1]:.2f}")
        print(f"최고가: ${hist['High'].max():.2f}")
        print(f"최저가: ${hist['Low'].min():.2f}")
        
        # ⭐ 재무 데이터 (yfinance 제공)
        print(f"\n💰 재무 데이터 (yfinance 제공):")
        
        financials = stock.quarterly_financials
        if financials is not None and not financials.empty:
            print(f"✅ 분기별 재무제표: {financials.shape}")
            print(f"\n항목 샘플:")
            print(financials.head(10))
        
        cashflow = stock.quarterly_cashflow
        if cashflow is not None and not cashflow.empty:
            print(f"\n✅ 현금흐름표 발견!")
            print(f"행 수: {len(cashflow)}")
            print(f"\n⭐ 현금흐름 항목:")
            print(cashflow.index.tolist())
            
            # OCF 찾기
            for idx in cashflow.index:
                if 'Operating' in str(idx) and 'Cash' in str(idx):
                    ocf_values = cashflow.loc[idx]
                    print(f"\n💰 영업활동 현금흐름 (OCF):")
                    print(f"  {idx}")
                    print(f"  최근 분기: ${ocf_values.iloc[0]:,.0f}")
                    break
        
        return {
            'success': True,
            'info': info,
            'price_days': len(hist),
            'has_financials': financials is not None,
            'has_cashflow': cashflow is not None,
        }
        
    except Exception as e:
        print(f"❌ 에러: {e}")
        return {'success': False, 'error': str(e)}


def test_edgar_data(ticker='AAPL'):
    """
    Step 2: EDGAR API로 상세 재무 데이터
    """
    print("\n" + "="*60)
    print(f"Step 2: EDGAR API 데이터 - {ticker}")
    print("="*60)
    
    try:
        # Ticker → CIK 변환
        mapper = StockMapper()
        cik = mapper.ticker_to_cik.get(ticker)
        
        if not cik:
            print(f"❌ {ticker}의 CIK를 찾을 수 없습니다")
            return {'success': False}
        
        print(f"✅ CIK: {cik}")
        
        # EDGAR 클라이언트
        edgar = EdgarClient(user_agent="Newturn support@newturn.com")
        
        # 기업 정보
        submissions = edgar.get_submissions(cik=cik)
        print(f"✅ 기업명: {submissions['name']}")
        print(f"✅ 거래소: {submissions.get('exchanges', ['N/A'])}")
        
        # Company Facts (재무 데이터)
        facts = edgar.get_company_facts(cik=cik)
        
        us_gaap_facts = facts['facts']['us-gaap']
        print(f"\n✅ US-GAAP 항목 수: {len(us_gaap_facts)}")
        
        # ⭐ 현금흐름 관련 항목 찾기
        cashflow_items = [
            'NetCashProvidedByUsedInOperatingActivities',  # OCF
            'NetCashProvidedByUsedInInvestingActivities',  # ICF
            'PaymentsToAcquirePropertyPlantAndEquipment',  # CAPEX
        ]
        
        print(f"\n⭐ 현금흐름 데이터:")
        found_items = []
        
        for item in cashflow_items:
            if item in us_gaap_facts:
                data = us_gaap_facts[item]
                units = list(data['units'].keys())
                print(f"\n✅ {item}")
                print(f"   단위: {units}")
                
                # 최근 데이터
                if units:
                    recent_data = data['units'][units[0]][-5:]  # 최근 5개
                    print(f"   최근 데이터 수: {len(recent_data)}")
                    if recent_data:
                        latest = recent_data[-1]
                        print(f"   최근 값: {latest.get('val'):,} ({latest.get('end', 'N/A')})")
                
                found_items.append(item)
        
        success_rate = len(found_items) / len(cashflow_items) * 100
        
        print(f"\n📊 현금흐름 항목 발견율: {success_rate:.0f}% ({len(found_items)}/{len(cashflow_items)})")
        
        if success_rate >= 66:
            print("✅ EDGAR 데이터 사용 가능!")
        else:
            print("⚠️  일부 항목 누락, GPT-4 보완 필요")
        
        return {
            'success': True,
            'found_items': found_items,
            'success_rate': success_rate,
        }
        
    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def test_gpt4_analysis(ticker='AAPL', openai_api_key=None):
    """
    Step 3: GPT-4로 메이트 분석
    """
    print("\n" + "="*60)
    print(f"Step 3: GPT-4 메이트 분석 - {ticker}")
    print("="*60)
    
    if not openai_api_key:
        print("❌ OpenAI API 키 필요")
        return {'success': False}
    
    try:
        import openai
        openai.api_key = openai_api_key
        
        # 샘플 데이터 (실제로는 EDGAR/yfinance에서)
        apple_data = {
            "stock_name": "Apple Inc.",
            "ticker": "AAPL",
            "market_cap": 3_000_000_000_000,  # $3T
            "current_price": 180,
            "per": 30.5,
            "pbr": 45.2,
            "roe": 150.0,  # Apple은 ROE 매우 높음
            "debt_ratio": 120.5,
            "dividend_yield": 0.5,
            "revenue_growth_3y": 11.2,
            "eps_growth_3y": 15.8,
            "rd_ratio": 6.5,
        }
        
        # 벤저민 메이트 프롬프트
        prompt = f"""
당신은 벤저민 그레이엄의 투자 철학을 따르는 AI 분석가입니다.

기업: {apple_data['stock_name']}
PER: {apple_data['per']}
PBR: {apple_data['pbr']}
부채비율: {apple_data['debt_ratio']}%
배당수익률: {apple_data['dividend_yield']}%

안전마진 관점으로 평가하고 JSON으로:
{{
  "score": 0-100,
  "summary": "한 줄 요약",
  "reason": "3줄 이내 평가 이유 (쉬운 언어)",
  "caution": "주의사항",
  "score_detail": {{"undervalued": 0-100, "safety": 0-100, "dividend": 0-100}}
}}
"""
        
        print("🤖 GPT-4 분석 중...")
        
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "벤저민 그레이엄 스타일 투자 분석가"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        print(f"\n✅ 분석 완료!")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🎩 벤저민 메이트 분석")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"💯 점수: {result['score']}/100")
        print(f"📝 요약: {result['summary']}")
        print(f"📊 이유:\n{result['reason']}")
        if result.get('caution'):
            print(f"⚠️  주의: {result['caution']}")
        print(f"📈 세부: {result['score_detail']}")
        
        # 비용 계산
        tokens = response.usage.total_tokens
        cost = (tokens / 1000) * 0.04  # 대략
        
        print(f"\n💰 비용:")
        print(f"  토큰: {tokens:,}")
        print(f"  예상: ${cost:.4f}")
        
        return {
            'success': True,
            'result': result,
            'cost': cost,
        }
        
    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def test_cost_estimation():
    """
    Step 4: 전체 비용 추정
    """
    print("\n" + "="*60)
    print("Step 4: 비용 추정")
    print("="*60)
    
    # 미국 주요 거래소 종목 수
    nasdaq_count = 3500
    nyse_count = 2400
    total_stocks = nasdaq_count + nyse_count  # 약 6000개
    
    # 시가총액 상위 500개만 타겟
    target_stocks = 500
    
    cost_per_stock = 0.04  # GPT-4 메이트 분석 (3개 메이트)
    
    print(f"📊 미국 상장 주식:")
    print(f"  - NASDAQ: {nasdaq_count:,}개")
    print(f"  - NYSE: {nyse_count:,}개")
    print(f"  - 총: {total_stocks:,}개")
    
    print(f"\n🎯 타겟: 시가총액 상위 {target_stocks}개")
    
    print(f"\n💰 비용 추정:")
    print(f"  종목당: ${cost_per_stock}")
    print(f"  {target_stocks}개: ${cost_per_stock * target_stocks:.2f}")
    print(f"  분기 업데이트 (4회/년): ${cost_per_stock * target_stocks * 4:.2f}")
    
    print(f"\n💡 캐싱 전략:")
    print(f"  - 최초 분석: ${cost_per_stock * target_stocks:.2f}")
    print(f"  - 이후: 재무제표 발표 시에만 재분석")
    print(f"  - 연간: ${cost_per_stock * target_stocks * 4:.2f} (관리 가능!)")


if __name__ == "__main__":
    print("="*60)
    print("🧪 POC: 미국 주식 데이터 수집 전체 테스트")
    print("="*60)
    
    # 테스트 종목
    ticker = 'AAPL'
    
    print(f"\n📍 테스트 종목: {ticker} (Apple)")
    print(f"{'='*60}\n")
    
    # Step 1: yfinance
    yf_result = test_yfinance_data(ticker)
    
    if yf_result['success']:
        print(f"\n✅ yfinance: 성공")
        print(f"  - 주가 데이터: {yf_result['price_days']}일")
        print(f"  - 재무제표: {'있음' if yf_result['has_financials'] else '없음'}")
        print(f"  - 현금흐름표: {'있음' if yf_result['has_cashflow'] else '없음'}")
    
    # Step 2: EDGAR
    edgar_result = test_edgar_data(ticker)
    
    if edgar_result['success']:
        print(f"\n✅ EDGAR: 성공")
        print(f"  - 현금흐름 항목: {edgar_result['success_rate']:.0f}%")
    
    # Step 3: GPT-4 (선택)
    openai_key = input("\n\nGPT-4 메이트 분석 테스트? OpenAI API 키 입력 (Skip하려면 Enter): ").strip()
    
    if openai_key:
        gpt4_result = test_gpt4_analysis(ticker, openai_key)
        
        if gpt4_result['success']:
            print(f"\n✅ GPT-4 메이트 분석: 성공")
            print(f"  - 비용: ${gpt4_result['cost']:.4f}")
    
    # Step 4: 비용 추정
    test_cost_estimation()
    
    # 최종 결론
    print("\n" + "="*60)
    print("📊 최종 결론")
    print("="*60)
    
    if yf_result['success'] and yf_result.get('has_cashflow'):
        print("\n✅ yfinance만으로도 충분!")
        print("  → OCF/FCF 데이터 제공")
        print("  → 무료")
        print("  → 간단한 API")
        print("\n🎯 권장: yfinance 우선 사용")
    
    elif edgar_result.get('success') and edgar_result.get('success_rate', 0) >= 66:
        print("\n✅ EDGAR API 사용 가능")
        print("  → 현금흐름 데이터 66%+ 커버")
        print("  → 무료")
        print("\n🎯 권장: EDGAR + yfinance 조합")
    
    else:
        print("\n⚠️  GPT-4 보완 필요")
        print("  → yfinance/EDGAR로 부족한 부분")
        print("  → GPT-4로 추출")
        print(f"  → 비용: 연간 ~${20 * 500 * 4:.0f}")
    
    print("\n" + "="*60)
    print("✅ POC 완료!")
    print("="*60)
    
    print("\n📝 다음 단계:")
    print("  1. 10개 종목 추가 테스트")
    print("  2. 데이터 파이프라인 구축")
    print("  3. DB 저장 로직")
    print("  4. 스케줄러 (분기별 업데이트)")

