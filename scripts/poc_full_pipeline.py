"""
POC 종합: 전체 데이터 파이프라인 검증

테스트 시나리오:
1. DART에서 재무 데이터 추출 (OCF/FCF)
2. yfinance에서 주가 데이터 추출
3. GPT-4로 메이트 분석
4. 결과 DB 저장
5. API로 조회

종목: 삼성전자 (005930)
"""

import sys
import os
import django

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

import dart_fss as dart
import yfinance as yf
from datetime import datetime, timedelta
from apps.stocks.models import Stock, StockFinancialRaw, StockPrice
from apps.analysis.models import MateAnalysis
from core.utils.mate_engine import MateEngine


def step1_create_stock():
    """Step 1: 종목 생성"""
    print("\n" + "="*60)
    print("Step 1: 종목 생성")
    print("="*60)
    
    stock, created = Stock.objects.update_or_create(
        stock_code='005930',
        defaults={
            'stock_name': '삼성전자',
            'stock_name_en': 'Samsung Electronics',
            'country': 'kr',
            'exchange': 'kospi',
            'industry': '전자부품',
            'sector': 'IT',
            'description': '종합 전자 기업',
        }
    )
    
    if created:
        print(f"✅ 종목 생성: {stock}")
    else:
        print(f"✅ 종목 조회: {stock}")
    
    return stock


def step2_extract_financial_data(stock, dart_api_key):
    """Step 2: DART에서 재무 데이터 추출"""
    print("\n" + "="*60)
    print("Step 2: DART 재무 데이터 추출")
    print("="*60)
    
    try:
        dart.set_api_key(api_key=dart_api_key)
        corp_list = dart.get_corp_list()
        corp = corp_list.find_by_stock_code(stock_code=stock.stock_code)
        
        print(f"✅ 기업: {corp.corp_name}")
        
        # 2023년 3분기 재무제표
        fs = corp.extract_fs(
            bgn_de='20230701',
            end_de='20230930',
            report_tp='quarter',
            separate=False,
            lang='ko'
        )
        
        # 현금흐름표에서 OCF 추출 시도
        cf = fs['cf']
        accounts = cf.iloc[:, 0]
        
        # 영업활동 현금흐름 찾기
        ocf_value = None
        for idx, account in enumerate(accounts):
            if '영업활동' in str(account) and '현금' in str(account):
                col_names = [col for col, _ in cf.columns if len(str(col)) > 10]
                if col_names:
                    ocf_value = cf.iloc[idx][col_names[0]].iloc[0]
                    print(f"✅ OCF 발견: {account}")
                    print(f"💰 값: {ocf_value}")
                    break
        
        if ocf_value is None:
            print("⚠️  OCF를 자동으로 찾지 못했습니다")
            print("→ GPT-4 추출 방식 사용 권장")
            ocf_value = 50000000000000  # 샘플값
        
        # DB 저장
        financial, created = StockFinancialRaw.objects.update_or_create(
            stock=stock,
            disclosure_year=2023,
            disclosure_quarter=3,
            defaults={
                'disclosure_date': datetime(2023, 9, 30),
                'ocf': ocf_value,
                'data_source': 'DART',
            }
        )
        
        print(f"✅ 재무 데이터 저장: {financial}")
        return financial
        
    except Exception as e:
        print(f"❌ DART 추출 실패: {e}")
        print("→ 샘플 데이터로 진행")
        
        # 샘플 데이터 저장
        financial, _ = StockFinancialRaw.objects.update_or_create(
            stock=stock,
            disclosure_year=2023,
            disclosure_quarter=3,
            defaults={
                'disclosure_date': datetime(2023, 9, 30),
                'revenue': 70000000000000,
                'net_income': 10000000000000,
                'ocf': 50000000000000,
                'fcf': 30000000000000,
                'data_source': 'SAMPLE',
            }
        )
        return financial


def step3_extract_price_data(stock):
    """Step 3: 주가 데이터 추출"""
    print("\n" + "="*60)
    print("Step 3: 주가 데이터 추출")
    print("="*60)
    
    try:
        # yfinance로 주가 가져오기
        ticker = yf.Ticker('005930.KS')  # 코스피는 .KS
        
        # 최근 30일
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        hist = ticker.history(
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d')
        )
        
        print(f"✅ 주가 데이터 {len(hist)}일치 추출")
        
        # 최근 가격만 저장 (샘플)
        if len(hist) > 0:
            latest = hist.iloc[-1]
            latest_date = hist.index[-1].date()
            
            price, created = StockPrice.objects.update_or_create(
                stock=stock,
                date=latest_date,
                defaults={
                    'close_price': latest['Close'],
                    'volume': latest['Volume'],
                }
            )
            
            print(f"✅ 주가 저장: {price}")
            return price
        
    except Exception as e:
        print(f"⚠️  yfinance 실패: {e}")
        print("→ 샘플 데이터 사용")
        
        price, _ = StockPrice.objects.update_or_create(
            stock=stock,
            date=datetime.now().date(),
            defaults={
                'close_price': 70000,
                'volume': 10000000,
            }
        )
        return price


def step4_mate_analysis(stock, openai_api_key):
    """Step 4: GPT-4 메이트 분석"""
    print("\n" + "="*60)
    print("Step 4: GPT-4 메이트 분석")
    print("="*60)
    
    if not openai_api_key:
        print("❌ OpenAI API 키 필요")
        return None
    
    try:
        # 메이트 엔진 초기화
        import openai
        openai.api_key = openai_api_key
        
        engine = MateEngine()
        
        # 샘플 재무 데이터
        stock_data = {
            'stock_name': stock.stock_name,
            'pbr': 1.8,
            'roe': 12.3,
            'debt_ratio': 30.5,
            'current_ratio': 220,
            'dividend_yield': 2.5,
            'revenue_growth_3y': 8.5,
            'eps_growth_3y': 10.2,
            'rd_ratio': 7.5,
        }
        
        # 3개 메이트 분석
        mates = ['benjamin', 'fisher', 'greenblatt']
        results = []
        
        for mate_type in mates:
            print(f"\n🤖 {mate_type} 메이트 분석 중...")
            
            result = engine.analyze(stock_data, mate_type)
            
            # DB 저장
            analysis, created = MateAnalysis.objects.update_or_create(
                stock=stock,
                mate_type=mate_type,
                defaults={
                    'score': result['score'],
                    'summary': result['summary'],
                    'reason': result['reason'],
                    'caution': result.get('caution', ''),
                    'score_detail': result.get('score_detail', {}),
                }
            )
            
            print(f"✅ {mate_type}: {result['score']}점 - {result['summary']}")
            results.append(analysis)
        
        return results
        
    except Exception as e:
        print(f"❌ 메이트 분석 실패: {e}")
        return None


def step5_verify_api():
    """Step 5: API 확인"""
    print("\n" + "="*60)
    print("Step 5: API 동작 확인")
    print("="*60)
    
    print("\n📍 다음 URL들을 브라우저에서 확인하세요:")
    print()
    print("  Admin:")
    print("  → http://localhost:8000/admin")
    print()
    print("  API 문서:")
    print("  → http://localhost:8000/swagger")
    print()
    print("  종목 검색:")
    print("  → http://localhost:8000/api/stocks/search/?q=삼성")
    print()
    print("  삼성전자 분석:")
    print("  → http://localhost:8000/api/analysis/005930/")
    print()


if __name__ == "__main__":
    print("="*60)
    print("🧪 POC 종합: 전체 파이프라인 검증")
    print("="*60)
    
    # API 키 입력
    print("\n필요한 API 키:")
    dart_key = input("1. DART API 키 (없으면 Enter): ").strip()
    openai_key = input("2. OpenAI API 키 (필수): ").strip()
    
    if not openai_key:
        print("❌ OpenAI API 키는 필수입니다")
        exit(1)
    
    try:
        # Step 1: 종목 생성
        stock = step1_create_stock()
        
        # Step 2: 재무 데이터
        if dart_key:
            financial = step2_extract_financial_data(stock, dart_key)
        else:
            print("\n⚠️  DART 키 없음 → 샘플 데이터 사용")
            financial = step2_extract_financial_data(stock, None)
        
        # Step 3: 주가 데이터
        price = step3_extract_price_data(stock)
        
        # Step 4: 메이트 분석
        analyses = step4_mate_analysis(stock, openai_key)
        
        # Step 5: API 확인
        step5_verify_api()
        
        # 완료
        print("\n" + "="*60)
        print("✅ 전체 파이프라인 POC 완료!")
        print("="*60)
        
        print("\n📊 생성된 데이터:")
        print(f"  - 종목: {Stock.objects.count()}개")
        print(f"  - 재무 데이터: {StockFinancialRaw.objects.count()}개")
        print(f"  - 주가 데이터: {StockPrice.objects.count()}개")
        print(f"  - 메이트 분석: {MateAnalysis.objects.count()}개")
        
        print("\n🎯 다음 단계:")
        print("  1. API 확인 (브라우저에서)")
        print("  2. 프론트엔드 연동")
        print("  3. 추가 종목 테스트 (10개)")
        print("  4. 데이터 품질 검증")
        
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()

