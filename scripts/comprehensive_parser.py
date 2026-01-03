"""
종합 파서 v3

전략:
1. Item 1 (Business) - 경쟁 환경, 비즈니스 모델
2. Item 1A (Risk) - 리스크 요인
3. Item 7 (MD&A) - 경영진 분석, 전망

문장 단위 분류:
- 경쟁사 관련
- 공급망 관련
- 규제/지정학 관련
- 신제품 관련
- 재무 전망 관련
"""
import re
import json


class ComprehensiveParser:
    """종합 파서"""
    
    def __init__(self, ticker):
        self.ticker = ticker
        self.company_names = self.get_company_names(ticker)
    
    def get_company_names(self, ticker):
        """회사명 매핑 (자기 회사 제외용)"""
        
        mapping = {
            'AAPL': ['Apple', 'Apple Inc'],
            'META': ['Meta', 'Meta Platforms', 'Facebook'],
            'NVDA': ['NVIDIA', 'Nvidia'],
            'AMZN': ['Amazon', 'Amazon.com'],
            'TSLA': ['Tesla', 'Tesla Inc'],
            'GOOGL': ['Google', 'Alphabet'],
            'MSFT': ['Microsoft'],
        }
        
        return mapping.get(ticker, [ticker])
    
    def split_into_sentences(self, text):
        """문장 단위 분리"""
        
        # 간단한 문장 분리 (. ! ? 기준)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # 너무 짧은 문장 제외
        return [s.strip() for s in sentences if len(s) > 50]
    
    def classify_sentence(self, sentence):
        """문장 분류"""
        
        categories = []
        sentence_lower = sentence.lower()
        
        # 1. 경쟁 관련
        if any(word in sentence_lower for word in ['compet', 'rival', 'market share', 'versus', 'compared to']):
            categories.append('competition')
        
        # 2. 공급망 관련
        if any(word in sentence_lower for word in ['supplier', 'supply chain', 'manufacture', 'source', 'procurement']):
            categories.append('supply_chain')
        
        # 3. 규제/지정학
        if any(word in sentence_lower for word in ['regulation', 'tariff', 'sanction', 'export control', 'china', 'geopolitical']):
            categories.append('regulatory')
        
        # 4. 신제품/혁신
        if any(word in sentence_lower for word in ['launch', 'introduce', 'new product', 'innovation', 'development']):
            categories.append('innovation')
        
        # 5. 재무 전망
        if any(word in sentence_lower for word in ['expect', 'anticipate', 'guidance', 'forecast', 'project', 'plan to']):
            categories.append('forward_looking')
        
        # 6. 리스크
        if any(word in sentence_lower for word in ['risk', 'uncertainty', 'challenge', 'threat', 'concern']):
            categories.append('risk')
        
        # 7. 고객/시장
        if any(word in sentence_lower for word in ['customer', 'market', 'demand', 'adoption']):
            categories.append('market')
        
        return categories
    
    def is_valuable_sentence(self, sentence):
        """가치있는 문장인가?"""
        
        # 숫자 포함 (%, $, 연도)
        has_numbers = bool(re.search(r'\d+%|\$\d+|202\d|Q[1-4]', sentence))
        
        # 구체적 이름 포함
        has_proper_nouns = bool(re.search(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', sentence))
        
        # 자기 회사명만 나오는 건 제외
        only_self = all(name in sentence for name in self.company_names) and len(re.findall(r'\b[A-Z][a-z]+', sentence)) <= 3
        
        return (has_numbers or has_proper_nouns) and not only_self
    
    def extract_from_section(self, section_name):
        """섹션에서 추출"""
        
        try:
            with open(f'data/section_{self.ticker}_{section_name}.txt', 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            return {}
        
        sentences = self.split_into_sentences(text)
        
        categorized = {
            'competition': [],
            'supply_chain': [],
            'regulatory': [],
            'innovation': [],
            'forward_looking': [],
            'risk': [],
            'market': [],
        }
        
        for sentence in sentences[:1000]:  # 최대 1000문장
            
            # 가치있는 문장만
            if not self.is_valuable_sentence(sentence):
                continue
            
            # 분류
            categories = self.classify_sentence(sentence)
            
            # 각 카테고리에 추가
            for category in categories:
                if category in categorized and len(categorized[category]) < 20:  # 각 카테고리 최대 20개
                    categorized[category].append({
                        'sentence': sentence,
                        'section': section_name,
                        'length': len(sentence)
                    })
        
        return categorized
    
    def parse_all(self):
        """전체 파싱"""
        
        print(f"\n{'='*80}")
        print(f"🔬 {self.ticker} 종합 파싱")
        print('-'*80)
        
        results = {
            'ticker': self.ticker,
            'sections': {}
        }
        
        # 3개 섹션 모두 파싱
        for section in ['item_1_business', 'item_1a_risk_factors', 'item_7_mda']:
            print(f"   📄 {section} 파싱 중...")
            
            categorized = self.extract_from_section(section)
            
            total = sum(len(v) for v in categorized.values())
            print(f"      ✅ {total}개 인사이트 추출")
            
            results['sections'][section] = categorized
        
        # 전체 통계
        all_categories = {}
        for section_data in results['sections'].values():
            for category, items in section_data.items():
                if category not in all_categories:
                    all_categories[category] = []
                all_categories[category].extend(items)
        
        results['summary'] = {
            category: len(items)
            for category, items in all_categories.items()
        }
        
        print(f"\n   📊 전체 요약:")
        for category, count in results['summary'].items():
            if count > 0:
                print(f"      {category}: {count}개")
        
        return results


def parse_all_stocks(tickers):
    """모든 종목 파싱"""
    
    print("="*80)
    print("🎯 종합 파서 v3 - 전체 섹션 분석")
    print("="*80)
    print()
    print("전략:")
    print("  ✅ Item 1, 1A, 7 모두 활용")
    print("  ✅ 문장 단위 분류")
    print("  ✅ 자기 회사명 제외")
    print("  ✅ 숫자/고유명사 포함 문장만")
    print()
    
    all_results = {}
    
    for ticker in tickers:
        parser = ComprehensiveParser(ticker)
        result = parser.parse_all()
        all_results[ticker] = result
    
    # 저장
    with open('data/comprehensive_insights.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print("✅ 저장: data/comprehensive_insights.json")
    print("="*80)
    
    # 전체 통계
    print(f"\n{'='*80}")
    print("📊 전체 통계")
    print('='*80)
    
    for ticker, data in all_results.items():
        total = sum(data['summary'].values())
        print(f"\n{ticker}: {total}개 인사이트")
        
        for category, count in sorted(data['summary'].items(), key=lambda x: -x[1]):
            if count > 0:
                print(f"  {category}: {count}개")
    
    return all_results


if __name__ == "__main__":
    STOCKS = ['AAPL', 'META', 'NVDA', 'AMZN', 'TSLA']
    
    results = parse_all_stocks(STOCKS)
    
    # 샘플 출력
    print(f"\n{'='*80}")
    print("📋 샘플 인사이트 (AAPL)")
    print('='*80)
    
    if 'AAPL' in results:
        aapl = results['AAPL']
        
        # Item 1 경쟁 관련
        item1 = aapl['sections'].get('item_1_business', {})
        competition = item1.get('competition', [])
        
        if competition:
            print(f"\n🔍 경쟁 환경 (Item 1):")
            for item in competition[:3]:
                print(f"  - {item['sentence'][:150]}...")
        
        # Item 7 전망
        item7 = aapl['sections'].get('item_7_mda', {})
        forward = item7.get('forward_looking', [])
        
        if forward:
            print(f"\n🔮 경영진 전망 (Item 7):")
            for item in forward[:3]:
                print(f"  - {item['sentence'][:150]}...")
    
    print(f"\n{'='*80}")
    print("💡 이제 모든 섹션에서 체계적 추출!")
    print("="*80)

