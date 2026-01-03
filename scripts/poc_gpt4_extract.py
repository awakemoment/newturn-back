"""
POC #2: GPT-4로 재무 데이터 추출

목표: 사업보고서를 GPT-4에 넣어서 OCF/FCF 추출 가능한지 검증

방법:
1. DART에서 사업보고서 다운로드 (HTML/XML)
2. GPT-4 API로 텍스트 전송
3. OCF/FCF 추출

테스트 종목: 삼성전자 (005930)
"""

import openai
import dart_fss as dart
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta


def extract_cashflow_with_gpt4(stock_code='005930', year=2023, quarter=4, dart_api_key=None, openai_api_key=None):
    """
    GPT-4를 활용한 현금흐름 데이터 추출
    
    Returns:
        dict: {
            'success': bool,
            'data': {
                'ocf': int,
                'fcf': int,
                'capex': int
            },
            'cost': float,  # API 비용 (추정)
            'error': str or None
        }
    """
    result = {
        'success': False,
        'data': {},
        'cost': 0.0,
        'error': None
    }
    
    try:
        # 1. DART에서 사업보고서 가져오기
        if not dart_api_key:
            result['error'] = 'DART API 키 필요'
            return result
        
        dart.set_api_key(api_key=dart_api_key)
        corp_list = dart.get_corp_list()
        corp = corp_list.find_by_stock_code(stock_code=stock_code)
        
        print(f"✅ 기업: {corp.corp_name}")
        
        # 재무제표 추출
        target_date = datetime(year, quarter * 3, 1)
        fs = corp.extract_fs(
            bgn_de=target_date.strftime('%Y%m%d'),
            end_de=(target_date + relativedelta(months=3)).strftime('%Y%m%d'),
            report_tp='quarter',
            separate=False,
            lang='ko'
        )
        
        # 현금흐름표를 텍스트로 변환
        cf = fs['cf']
        cf_text = cf.to_string()
        
        print(f"✅ 현금흐름표 텍스트 추출 ({len(cf_text)} 글자)")
        
        # 2. GPT-4로 분석
        if not openai_api_key:
            result['error'] = 'OpenAI API 키 필요'
            return result
        
        openai.api_key = openai_api_key
        
        prompt = f"""
다음은 {corp.corp_name}의 {year}년 {quarter}분기 현금흐름표입니다.

{cf_text[:3000]}  # 처음 3000자만 (토큰 제한)

다음 정보를 추출하여 JSON 형식으로 답변해주세요:

1. 영업활동 현금흐름 (OCF)
2. 투자활동 현금흐름 (ICF) 
3. 잉여현금흐름 (FCF) = OCF + ICF
4. 설비투자 (CAPEX) - 투자활동 중 유형자산 취득

JSON 형식:
{{
  "ocf": 숫자만 (단위: 원),
  "icf": 숫자만,
  "fcf": 숫자만,
  "capex": 숫자만
}}

주의: 
- 모든 값은 원 단위로 변환
- 백만원이면 1,000,000 곱하기
- 음수는 그대로 표시
"""
        
        print(f"🤖 GPT-4 분석 중...")
        
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "재무제표 분석 전문가"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # 일관성 위해 낮게
            response_format={"type": "json_object"}
        )
        
        # 결과 파싱
        gpt_response = response.choices[0].message.content
        extracted_data = json.loads(gpt_response)
        
        print(f"✅ GPT-4 추출 완료!")
        print(f"📊 결과:")
        print(f"  - OCF: {extracted_data.get('ocf'):,}원")
        print(f"  - ICF: {extracted_data.get('icf'):,}원")
        print(f"  - FCF: {extracted_data.get('fcf'):,}원")
        print(f"  - CAPEX: {extracted_data.get('capex'):,}원")
        
        # 비용 계산
        tokens_used = response.usage.total_tokens
        cost_per_1k = 0.01 + 0.03  # input + output (대략)
        estimated_cost = (tokens_used / 1000) * cost_per_1k
        
        print(f"\n💰 API 비용:")
        print(f"  - 토큰 사용: {tokens_used:,}")
        print(f"  - 예상 비용: ${estimated_cost:.4f}")
        
        result['success'] = True
        result['data'] = extracted_data
        result['cost'] = estimated_cost
        
    except Exception as e:
        print(f"❌ 에러: {e}")
        result['error'] = str(e)
    
    return result


def test_multiple_stocks(stock_codes, dart_api_key, openai_api_key):
    """
    여러 종목 테스트
    """
    results = []
    total_cost = 0.0
    
    for stock_code in stock_codes:
        print(f"\n{'='*60}")
        print(f"테스트 종목: {stock_code}")
        print(f"{'='*60}")
        
        result = extract_cashflow_with_gpt4(
            stock_code=stock_code,
            year=2023,
            quarter=3,
            dart_api_key=dart_api_key,
            openai_api_key=openai_api_key
        )
        
        results.append({
            'stock_code': stock_code,
            'success': result['success'],
            'cost': result['cost'],
            'error': result['error']
        })
        
        total_cost += result['cost']
    
    # 종합 결과
    print(f"\n{'='*60}")
    print(f"📊 종합 결과")
    print(f"{'='*60}")
    
    success_count = sum(1 for r in results if r['success'])
    print(f"성공: {success_count}/{len(stock_codes)}")
    print(f"총 비용: ${total_cost:.4f}")
    print(f"종목당 평균: ${total_cost/len(stock_codes):.4f}")
    
    # 전체 종목 추정
    total_stocks_kr = 2000  # 한국 상장사 약 2000개
    estimated_total_cost = (total_cost / len(stock_codes)) * total_stocks_kr
    
    print(f"\n💡 전체 종목 추정:")
    print(f"  - 한국 전체 ({total_stocks_kr}개): ${estimated_total_cost:.2f}")
    print(f"  - 분기당 업데이트: ${estimated_total_cost:.2f}")
    print(f"  - 연간 (4분기): ${estimated_total_cost * 4:.2f}")
    
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 POC #1: DART + GPT-4 현금흐름 데이터 추출")
    print("=" * 60)
    print()
    
    # API 키 입력
    dart_key = input("DART API 키: ").strip()
    openai_key = input("OpenAI API 키: ").strip()
    
    if not dart_key or not openai_key:
        print("\n⚠️  두 API 키가 모두 필요합니다")
        exit(1)
    
    # 테스트 모드 선택
    print("\n테스트 모드:")
    print("1. 단일 종목 (삼성전자)")
    print("2. 다중 종목 (10개)")
    choice = input("선택 (1 or 2): ").strip()
    
    if choice == '1':
        # 단일 종목 테스트
        extract_cashflow_with_gpt4(
            stock_code='005930',
            year=2023,
            quarter=3,
            dart_api_key=dart_key,
            openai_api_key=openai_key
        )
    
    elif choice == '2':
        # 다중 종목 테스트
        test_stocks = [
            '005930',  # 삼성전자
            '000660',  # SK하이닉스
            '035720',  # 카카오
            '035420',  # NAVER
            '005380',  # 현대차
            '051910',  # LG화학
            '006400',  # 삼성SDI
            '028260',  # 삼성물산
            '012330',  # 현대모비스
            '009150',  # 삼성전기
        ]
        
        test_multiple_stocks(
            stock_codes=test_stocks,
            dart_api_key=dart_key,
            openai_api_key=openai_key
        )
    
    print("\n" + "=" * 60)
    print("✅ POC 완료!")
    print("=" * 60)
    print("\n다음 단계:")
    print("  1. 성공하면: 전체 파이프라인 구축")
    print("  2. 실패하면: 대안 검토 (유료 API 등)")

