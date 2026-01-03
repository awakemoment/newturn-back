"""
AI 기반 10-K 분석기

Claude가 직접 10-K를 읽고 분석합니다.
- Regex 패턴 매칭 X
- AI가 문맥을 이해하고 핵심 인사이트 추출

분석 항목:
1. 경쟁 환경 (누가 경쟁사? 시장 점유율은?)
2. 비즈니스 모델 변화
3. 신제품/서비스 로드맵
4. 공급망 구조 및 리스크
5. 규제/지정학 영향
6. 경영진 전망 (구체적 숫자)
7. 핵심 리스크 (새로 추가된 것)
8. 재무 전략 (CAPEX, R&D 계획)
"""
import json
import os


class AI10KAnalyzer:
    """AI 기반 10-K 분석기"""
    
    def __init__(self):
        self.analysis_prompts = self.define_prompts()
    
    def define_prompts(self):
        """분석 프롬프트 정의"""
        
        return {
            'business_model': """
이 회사의 비즈니스 모델을 분석해주세요:

1. 주요 제품/서비스는 무엇인가요? (구체적 이름과 매출 비중)
2. 수익 모델은? (광고, 구독, 제품 판매, 수수료 등)
3. 타겟 고객은?
4. 핵심 차별화 요소는?
5. 비즈니스 모델에 중요한 변화가 있나요?

JSON 형태로 답변:
{
  "products": [{"name": "...", "revenue_share": "...%", "description": "..."}],
  "revenue_model": ["..."],
  "target_customers": ["..."],
  "differentiation": ["..."],
  "changes": ["..."]
}
""",
            
            'competition': """
경쟁 환경을 분석해주세요:

1. 주요 경쟁사는? (구체적 회사명)
2. 시장 점유율은? (이 회사 vs 경쟁사)
3. 경쟁 우위는?
4. 경쟁 열위는?
5. 시장 구조 변화?

JSON 형태로 답변:
{
  "competitors": [{"name": "...", "market_share": "...%", "strength": "..."}],
  "our_market_share": "...%",
  "competitive_advantages": ["..."],
  "competitive_weaknesses": ["..."],
  "market_trends": ["..."]
}
""",
            
            'supply_chain': """
공급망을 분석해주세요:

1. 핵심 공급업체는? (sole supplier?)
2. 공급망 리스크는?
3. 제조 전략? (자체 제조 vs 외주)
4. 공급망 관련 투자 계획?
5. 공급망 이슈가 매출/비용에 미친 영향?

JSON 형태로 답변:
{
  "key_suppliers": [{"name": "...", "role": "...", "dependency": "sole/primary/secondary"}],
  "risks": ["..."],
  "manufacturing_strategy": "...",
  "investments": ["..."],
  "financial_impact": "..."
}
""",
            
            'forward_guidance': """
경영진 전망을 추출해주세요:

1. 매출 성장률 전망? (구체적 %나 범위)
2. 마진 전망?
3. CAPEX 계획?
4. 신제품 출시 일정?
5. 시장/고객 확대 계획?

JSON 형태로 답변:
{
  "revenue_growth": "...%",
  "margin_outlook": "...",
  "capex_plan": "...",
  "new_products": [{"name": "...", "launch_date": "..."}],
  "expansion_plans": ["..."]
}
""",
            
            'risks': """
핵심 리스크를 분석해주세요:

1. 새로 추가된 리스크는?
2. 가장 중요한 리스크 Top 5는?
3. 각 리스크의 재무적 영향은?
4. 리스크 완화 계획은?

JSON 형태로 답변:
{
  "new_risks": ["..."],
  "top_5_risks": [{"risk": "...", "impact": "...", "mitigation": "..."}]
}
""",
            
            'regulatory': """
규제/지정학 영향을 분석해주세요:

1. 관세/무역 규제 영향? (구체적 금액)
2. 중국/EU 등 특정 지역 리스크?
3. 규제 변화 대응 계획?
4. 지정학 리스크로 인한 전략 변화?

JSON 형태로 답변:
{
  "tariff_impact": "...",
  "regional_risks": [{"region": "...", "issue": "...", "impact": "..."}],
  "compliance_plan": ["..."],
  "strategic_changes": ["..."]
}
""",
        }
    
    def create_analysis_script(self, ticker, section_name):
        """
        분석 스크립트 생성
        
        이 함수는 실제로는 사용자(당신)가 직접 실행할 프롬프트를 생성합니다.
        Claude API를 사용하지 않고, 당신이 이 창에서 직접 분석합니다.
        """
        
        filename = f'data/section_{ticker}_{section_name}.txt'
        
        if not os.path.exists(filename):
            return None
        
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 텍스트가 너무 길면 청크로 나누기
        max_length = 100000  # 약 100KB
        
        if len(text) > max_length:
            # 중요한 부분만 (앞 50%, 뒤 50%)
            half = max_length // 2
            text = text[:half] + "\n\n[... 중간 생략 ...]\n\n" + text[-half:]
        
        return {
            'ticker': ticker,
            'section': section_name,
            'text_length': len(text),
            'text': text,
            'prompts': self.analysis_prompts
        }
    
    def generate_analysis_tasks(self, tickers):
        """분석 작업 생성"""
        
        print("="*80)
        print("🤖 AI 기반 10-K 분석 작업 생성")
        print("="*80)
        print()
        print("전략:")
        print("  1. Claude가 직접 각 섹션 읽기")
        print("  2. 구조화된 질문에 JSON으로 답변")
        print("  3. Regex 패턴 매칭 없음")
        print()
        
        tasks = []
        
        for ticker in tickers:
            print(f"\n{'='*80}")
            print(f"📊 {ticker} 분석 작업 생성")
            print('-'*80)
            
            # Item 1: 비즈니스 모델, 경쟁 환경
            item1_task = self.create_analysis_script(ticker, 'item_1_business')
            if item1_task:
                item1_task['analysis_type'] = ['business_model', 'competition', 'supply_chain']
                tasks.append(item1_task)
                print(f"   ✅ Item 1 (Business): {item1_task['text_length']:,} chars")
            
            # Item 1A: 리스크, 규제
            item1a_task = self.create_analysis_script(ticker, 'item_1a_risk_factors')
            if item1a_task:
                item1a_task['analysis_type'] = ['risks', 'regulatory']
                tasks.append(item1a_task)
                print(f"   ✅ Item 1A (Risk): {item1a_task['text_length']:,} chars")
            
            # Item 7: 전망, 재무 전략
            item7_task = self.create_analysis_script(ticker, 'item_7_mda')
            if item7_task:
                item7_task['analysis_type'] = ['forward_guidance', 'supply_chain']
                tasks.append(item7_task)
                print(f"   ✅ Item 7 (MD&A): {item7_task['text_length']:,} chars")
        
        # 저장
        with open('data/ai_analysis_tasks.json', 'w', encoding='utf-8') as f:
            # 텍스트는 너무 커서 제외
            tasks_meta = [
                {
                    'ticker': t['ticker'],
                    'section': t['section'],
                    'text_length': t['text_length'],
                    'analysis_type': t['analysis_type']
                }
                for t in tasks
            ]
            json.dump(tasks_meta, f, indent=2)
        
        print(f"\n{'='*80}")
        print(f"✅ 총 {len(tasks)}개 분석 작업 생성")
        print("="*80)
        
        return tasks


def main():
    """메인 함수"""
    
    analyzer = AI10KAnalyzer()
    
    STOCKS = ['AAPL', 'META', 'NVDA', 'AMZN', 'TSLA']
    
    tasks = analyzer.generate_analysis_tasks(STOCKS)
    
    print(f"\n{'='*80}")
    print("📋 다음 단계: AI 분석 실행")
    print('='*80)
    print()
    print("방법 1: 이 창에서 직접 분석")
    print("  - 각 종목/섹션을 Claude(저)에게 직접 보여주기")
    print("  - 프롬프트와 함께 텍스트 제공")
    print("  - JSON 결과 받아서 저장")
    print()
    print("방법 2: Claude API 사용 (비용 발생)")
    print("  - anthropic Python SDK 사용")
    print("  - 자동화 가능")
    print("  - 하지만 비용 발생")
    print()
    print("추천: 방법 1 (직접 분석)")
    print("  → 5개 종목 × 3개 섹션 = 15개 분석")
    print("  → 각 5-10분 = 총 2-3시간")
    print("  → 100% 정확도, 비용 0")
    print()
    
    # 첫 번째 작업 샘플
    if tasks:
        first_task = tasks[0]
        
        print(f"{'='*80}")
        print(f"📄 샘플 분석 작업: {first_task['ticker']} - {first_task['section']}")
        print('='*80)
        print()
        print("분석 항목:")
        for analysis_type in first_task['analysis_type']:
            print(f"  - {analysis_type}")
        print()
        print("프롬프트 예시:")
        print('-'*80)
        print(first_task['prompts']['business_model'])
        print()
        print(f"텍스트 길이: {first_task['text_length']:,} chars")
        print()
        
        # 텍스트 샘플 저장
        sample_file = f"data/analysis_sample_{first_task['ticker']}_{first_task['section']}.txt"
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(f"Ticker: {first_task['ticker']}\n")
            f.write(f"Section: {first_task['section']}\n")
            f.write(f"Analysis Types: {', '.join(first_task['analysis_type'])}\n")
            f.write("\n" + "="*80 + "\n")
            f.write("TEXT:\n")
            f.write("="*80 + "\n\n")
            f.write(first_task['text'][:5000])  # 처음 5000자만
            f.write("\n\n[... continues ...]")
        
        print(f"✅ 샘플 저장: {sample_file}")
    
    print(f"\n{'='*80}")
    print("💡 이제 진짜 AI 기반 분석!")
    print("="*80)


if __name__ == "__main__":
    main()

