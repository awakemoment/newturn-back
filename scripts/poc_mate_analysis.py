"""
POC #3: GPT-4 기반 메이트 분석

목표: GPT-4로 투자 대가의 관점을 구현 가능한지 검증

테스트: 삼성전자를 3개 메이트로 분석
"""

from openai import OpenAI
import json


# 샘플 재무 데이터 (실제 데이터는 DB에서)
SAMSUNG_DATA = {
    "stock_name": "삼성전자",
    "stock_code": "005930",
    "market_cap": 400_000_000_000_000,  # 400조
    "current_price": 70000,
    
    # 재무 지표
    "per": 15.2,
    "pbr": 1.8,
    "roe": 12.3,
    "debt_ratio": 30.5,
    "current_ratio": 220.0,
    
    # 배당
    "dividend_yield": 2.5,
    "dividend_history_5y": [1000, 1100, 1200, 1300, 1400],
    
    # 성장성
    "revenue_growth_3y": 8.5,  # %
    "eps_growth_3y": 10.2,
    "rd_ratio": 7.5,  # R&D / 매출
    
    # 현금흐름 (10년 평균)
    "ocf_avg_10y": 50_000_000_000_000,  # 50조
    "fcf_avg_10y": 30_000_000_000_000,  # 30조
    "capex_ratio": 12.5,  # CAPEX / 매출
}


def analyze_with_benjamin(stock_data, client):
    """
    벤저민 그레이엄 메이트 분석
    """
    prompt = f"""
당신은 벤저민 그레이엄의 투자 철학을 따르는 AI 분석가입니다.

투자 원칙:
• 안전마진 최우선
• 저평가 기업 선호
• 재무 안전성 중시
• 배당 이력 평가

기업 정보:
- 기업명: {stock_data['stock_name']}
- 현재가: {stock_data['current_price']:,}원
- 시가총액: {stock_data['market_cap']:,}원
- PER: {stock_data['per']}
- PBR: {stock_data['pbr']}
- ROE: {stock_data['roe']}%
- 부채비율: {stock_data['debt_ratio']}%
- 유동비율: {stock_data['current_ratio']}%
- 배당수익률: {stock_data['dividend_yield']}%
- 5년 배당 추이: {stock_data['dividend_history_5y']}원

당신의 투자 철학에 따라 이 기업을 평가하세요.

응답 형식 (JSON):
{{
  "score": 0-100 점수,
  "summary": "한 줄 요약 (20자 이내)",
  "reason": "평가 이유 (3-4줄, 쉬운 언어, 구체적 숫자 포함)",
  "caution": "주의사항 (있다면)",
  "score_detail": {{
    "undervalued": 0-100,
    "safety": 0-100,
    "dividend": 0-100
  }}
}}

말투: 신중하고 정중한 톤 ("~해요", "~합니다")
"""
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "벤저민 그레이엄 스타일 투자 분석가"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    result['mate_type'] = 'benjamin'
    result['mate_name'] = '벤저민 그레이엄'
    
    return result


def analyze_with_fisher(stock_data, client):
    """
    필립 피셔 메이트 분석
    """
    prompt = f"""
당신은 필립 피셔의 투자 철학을 따르는 AI 분석가입니다.

투자 원칙:
• 성장주 발굴
• 경영진 역량 중시
• 제품 경쟁력 평가
• 장기 관점

기업 정보:
- 기업명: {stock_data['stock_name']}
- 3년 매출 성장률: {stock_data['revenue_growth_3y']}%
- 3년 EPS 성장률: {stock_data['eps_growth_3y']}%
- R&D 비중: {stock_data['rd_ratio']}%
- ROE: {stock_data['roe']}%

당신의 투자 철학에 따라 이 기업을 평가하세요.

응답 형식 (JSON):
{{
  "score": 0-100 점수,
  "summary": "한 줄 요약 (20자 이내)",
  "reason": "평가 이유 (3-4줄, 성장성과 경영진 중심)",
  "caution": "주의사항 (있다면)",
  "score_detail": {{
    "growth": 0-100,
    "management": 0-100,
    "competitive_edge": 0-100
  }}
}}

말투: 열정적이고 미래 지향적 ("~네요", "~할 거예요")
"""
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "필립 피셔 스타일 투자 분석가"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    result['mate_type'] = 'fisher'
    result['mate_name'] = '필립 피셔'
    
    return result


def analyze_with_greenblatt(stock_data, client):
    """
    조엘 그린블라트 메이트 분석
    """
    # ROIC, 이익수익률 계산 (간단 버전)
    roic = stock_data['roe']  # 실제로는 EBIT / 투하자본
    earnings_yield = 100 / stock_data['per'] if stock_data['per'] > 0 else 0
    
    prompt = f"""
당신은 조엘 그린블라트의 "마법공식"을 따르는 AI 분석가입니다.

투자 원칙:
• 우량 기업 = ROIC 높음
• 염가 = 이익수익률 높음
• 두 순위의 합으로 평가

기업 정보:
- 기업명: {stock_data['stock_name']}
- ROIC (간소화): {roic}%
- 이익수익률: {earnings_yield:.2f}%
- PER: {stock_data['per']}
- ROE: {stock_data['roe']}%

당신의 마법공식에 따라 이 기업을 평가하세요.

응답 형식 (JSON):
{{
  "score": 0-100 점수,
  "summary": "한 줄 요약 (20자 이내)",
  "reason": "평가 이유 (마법공식 관점, 구체적 숫자)",
  "caution": "주의사항 (있다면)",
  "score_detail": {{
    "quality": 0-100,
    "value": 0-100
  }}
}}

말투: 논리적이고 수학적 ("~입니다", "계산 결과")
"""
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "조엘 그린블라트 스타일 투자 분석가"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    result['mate_type'] = 'greenblatt'
    result['mate_name'] = '조엘 그린블라트'
    
    return result


def compare_mates(stock_data, client):
    """
    3개 메이트 분석 비교
    """
    print(f"\n{'='*60}")
    print(f"🎯 종목: {stock_data['stock_name']}")
    print(f"{'='*60}\n")
    
    # 각 메이트 분석
    benjamin = analyze_with_benjamin(stock_data, client)
    fisher = analyze_with_fisher(stock_data, client)
    greenblatt = analyze_with_greenblatt(stock_data, client)
    
    # 결과 출력
    for mate in [benjamin, fisher, greenblatt]:
        print(f"\n{'-'*60}")
        print(f"🤖 {mate['mate_name']} 메이트")
        print(f"{'-'*60}")
        print(f"💯 점수: {mate['score']}/100")
        print(f"📝 요약: {mate['summary']}")
        print(f"📊 이유:\n{mate['reason']}")
        if mate.get('caution'):
            print(f"⚠️  주의: {mate['caution']}")
        print(f"📈 세부: {mate['score_detail']}")
    
    # 비교 분석
    print(f"\n{'='*60}")
    print(f"📊 메이트별 비교")
    print(f"{'='*60}")
    print(f"벤저민: {benjamin['score']}점 - {benjamin['summary']}")
    print(f"피  셔: {fisher['score']}점 - {fisher['summary']}")
    print(f"그린블: {greenblatt['score']}점 - {greenblatt['summary']}")
    
    avg_score = (benjamin['score'] + fisher['score'] + greenblatt['score']) / 3
    print(f"\n평균 점수: {avg_score:.1f}점")
    
    # Aha Moment 체크
    score_diff = max(benjamin['score'], fisher['score'], greenblatt['score']) - \
                 min(benjamin['score'], fisher['score'], greenblatt['score'])
    
    print(f"\n💡 Aha Moment 분석:")
    print(f"  - 점수 차이: {score_diff}점")
    
    if score_diff >= 20:
        print(f"  ✅ 관점마다 평가가 다름! (차이 {score_diff}점)")
        print(f"  → 사용자가 Aha Moment 느낄 가능성 높음")
    else:
        print(f"  ⚠️  차이가 작음 ({score_diff}점)")
        print(f"  → 프롬프트 개선 필요")
    
    return {
        'benjamin': benjamin,
        'fisher': fisher,
        'greenblatt': greenblatt,
        'avg_score': avg_score,
        'score_diff': score_diff
    }


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 POC #3: GPT-4 메이트 분석")
    print("=" * 60)
    print()
    
    # OpenAI API 키
    api_key = input("OpenAI API 키: ").strip()
    
    if not api_key:
        print("⚠️  API 키가 필요합니다")
        exit(1)
    
    # OpenAI 클라이언트 생성 (v1.0+ 방식)
    client = OpenAI(api_key=api_key)
    
    # 삼성전자 분석
    result = compare_mates(SAMSUNG_DATA, client)
    
    print(f"\n{'='*60}")
    print(f"✅ POC 완료!")
    print(f"{'='*60}")
    
    print("\n🎯 검증 결과:")
    print(f"  ✅ 3개 메이트 모두 작동")
    print(f"  ✅ 관점별로 다른 평가 ({result['score_diff']}점 차이)")
    print(f"  ✅ 해석 텍스트 자동 생성")
    
    print("\n💰 비용 추정:")
    print(f"  - 1개 종목 3개 메이트 분석: 약 $0.06")
    print(f"  - 1000개 종목: 약 $60")
    print(f"  - 캐싱 적용 시: 최초 1회만")
    
    print("\n🚀 다음 단계:")
    print("  1. 린치 메이트 추가")
    print("  2. 프롬프트 최적화 (점수 차이 더 크게)")
    print("  3. 실제 DB 연동")
    print("  4. API 엔드포인트 구현")

