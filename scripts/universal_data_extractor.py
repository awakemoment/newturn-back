"""
범용 10-K 데이터 추출기

목표: 숫자가 아닌 정성적 인사이트 100% 추출

추출 대상:
1. 경쟁사 언급 및 시장 점유율
2. 신제품/서비스 로드맵
3. 공급망 구체 정보
4. 경영진 전망 및 가이던스
5. 고객 집중도
6. 지정학/규제 영향
7. 핵심 파트너십
8. M&A 계획
9. 구조조정/비용 절감
10. 신규 리스크

추출 방법:
- 패턴 매칭
- 문맥 기반 추출
- 엔티티 인식
- 관계 추출
"""
import re
import json


class UniversalDataExtractor:
    """범용 데이터 추출기"""
    
    def __init__(self):
        self.patterns = self.define_patterns()
    
    def define_patterns(self):
        """추출 패턴 정의"""
        
        return {
            # 1. 경쟁사 언급
            'competitors': {
                'patterns': [
                    r'([\w\s]+)\s+(?:is|are|has|have)\s+(?:our|a|the)\s+(?:main|primary|key|major)?\s*(?:competitor|competition)',
                    r'(?:compete|competing)\s+(?:with|against)\s+([\w\s,&]+)',
                    r'([\w]+)(?:\'s)?\s+market share',
                    r'versus\s+([\w\s]+)',
                ],
                'keywords': ['Samsung', 'Huawei', 'AMD', 'Intel', 'AWS', 'Azure', 'TikTok', 'BYD']
            },
            
            # 2. 시장 점유율
            'market_share': {
                'patterns': [
                    r'market share.*?(\d+(?:\.\d+)?)\s*(?:%|percent|percentage)',
                    r'(\d+(?:\.\d+)?)\s*(?:%|percent)\s+(?:of|market|share)',
                    r'(?:declined|increased|grew)\s+(?:from|to)\s+(\d+)\s*%\s+to\s+(\d+)\s*%',
                ],
            },
            
            # 3. 신제품 로드맵
            'product_roadmap': {
                'patterns': [
                    r'(?:expect to|plan to|will)\s+(?:launch|introduce|release)\s+([\w\s]+)',
                    r'(?:launching|releasing)\s+([\w\s]+)\s+in\s+(Q[1-4]|[Jj]anuary|[Ff]ebruary|202\d)',
                    r'new product.*?([\w\s]+)',
                ],
                'keywords': ['launch', 'introduce', 'release', 'unveil', 'announce']
            },
            
            # 4. 공급망 구체 정보
            'supply_chain': {
                'patterns': [
                    r'([\w\s]+)\s+(?:is|are)\s+(?:our|the)\s+(?:sole|single|primary|main)\s+(?:supplier|source|manufacturer)',
                    r'(?:sole|single)\s+source.*?([\w\s]+)',
                    r'supply\s+(?:constraint|shortage|disruption).*?(?:cost|impact|loss).*?\$?([\d,\.]+)\s*(?:billion|million)',
                ],
            },
            
            # 5. 경영진 전망 (Forward-looking)
            'management_guidance': {
                'patterns': [
                    r'(?:expect|anticipate|forecast|project|plan)\s+(?:to|that)?\s*.{0,100}?(\d+(?:\.\d+)?)\s*(?:%|percent)',
                    r'guidance.*?(\d+(?:\.\d+)?)\s*(?:%|percent)',
                    r'(?:will|should)\s+(?:grow|increase|decline)\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*(?:%|percent)',
                ],
                'keywords': ['expect', 'anticipate', 'forecast', 'guidance', 'outlook', 'project']
            },
            
            # 6. 고객 집중도
            'customer_concentration': {
                'patterns': [
                    r'(?:top|largest)\s+(\d+)\s+customer.*?(?:account|represent).*?(\d+)\s*(?:%|percent)',
                    r'(\d+)\s*%.*?(?:from|by)\s+(?:top|largest|single)\s+customer',
                ],
            },
            
            # 7. 지정학/관세 영향
            'geopolitical_impact': {
                'patterns': [
                    r'tariff.*?(?:\$|cost|impact).*?([\d,\.]+)\s*(?:billion|million)',
                    r'(?:China|Chinese|trade)\s+(?:restriction|ban|sanction|tariff).*?(?:impact|cost|loss)',
                    r'export\s+control.*?(?:impact|affect|limit)',
                ],
                'keywords': ['tariff', 'China', 'export control', 'sanction', 'trade war', 'geopolitical']
            },
            
            # 8. R&D 집중 분야
            'rd_focus': {
                'patterns': [
                    r'R&D.*?(?:focus|invest|spend).*?(?:on|in)\s+([\w\s,]+)',
                    r'(?:developing|building|creating)\s+([\w\s]+)\s+(?:technology|product|platform)',
                ],
                'keywords': ['AI', 'machine learning', 'autonomous', 'quantum', 'AR/VR', 'metaverse']
            },
            
            # 9. M&A 및 투자
            'ma_activity': {
                'patterns': [
                    r'(?:acquired|acquisition of)\s+([\w\s\.]+)\s+(?:for|in)\s+\$?([\d,\.]+)\s*(?:billion|million)',
                    r'invest(?:ed|ment)?\s+\$?([\d,\.]+)\s*(?:billion|million)\s+in\s+([\w\s]+)',
                ],
            },
            
            # 10. 구조조정/비용 절감
            'restructuring': {
                'patterns': [
                    r'(?:layoff|restructur|cost\s+reduction|headcount\s+reduction).*?(\d+(?:,\d+)?)\s+(?:employee|people|position)',
                    r'(?:save|reduce|cut)\s+(?:cost|expense).*?\$?([\d,\.]+)\s*(?:billion|million)',
                ],
                'keywords': ['layoff', 'restructuring', 'cost reduction', 'efficiency']
            },
        }
    
    def extract_from_text(self, text, ticker):
        """텍스트에서 모든 인사이트 추출"""
        
        results = {
            'ticker': ticker,
            'extracted': {}
        }
        
        for category, config in self.patterns.items():
            findings = []
            
            # 패턴 매칭
            for pattern in config.get('patterns', []):
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    # 매치된 문장 전체 추출
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end]
                    
                    findings.append({
                        'matched': match.group(0),
                        'context': context.strip(),
                        'position': match.start()
                    })
            
            # 키워드 기반 추출
            if 'keywords' in config:
                for keyword in config['keywords']:
                    pattern = r'.{0,150}' + re.escape(keyword) + r'.{0,150}'
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        findings.append({
                            'keyword': keyword,
                            'context': match.group(0).strip(),
                            'position': match.start()
                        })
            
            # 중복 제거 (같은 위치 근처)
            unique_findings = []
            positions = set()
            
            for finding in findings[:50]:  # 최대 50개
                pos = finding.get('position', 0)
                # 500자 이내 중복 제거
                if not any(abs(pos - p) < 500 for p in positions):
                    unique_findings.append(finding)
                    positions.add(pos)
            
            results['extracted'][category] = unique_findings[:10]  # 각 카테고리 최대 10개
        
        return results
    
    def extract_all_stocks(self, tickers):
        """모든 종목 추출"""
        
        print("="*80)
        print("🔬 범용 데이터 추출기 실행")
        print("="*80)
        print()
        print("목표: 10-K 내 모든 정성적 인사이트 추출")
        print("     (숫자 테이블이 아닌 문장/문맥 정보)")
        print()
        
        all_results = {}
        
        for ticker in tickers:
            print(f"\n{'='*80}")
            print(f"📊 {ticker} 추출 중...")
            print('-'*80)
            
            # Item 7 (MD&A) 읽기
            filename = f'data/section_{ticker}_item_7_mda.txt'
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # 추출
                result = self.extract_from_text(text, ticker)
                
                # 결과 요약
                total_findings = sum(len(v) for v in result['extracted'].values())
                
                print(f"   ✅ 총 {total_findings}개 인사이트 발견")
                
                # 카테고리별 미리보기
                for category, findings in result['extracted'].items():
                    if findings:
                        print(f"      {category}: {len(findings)}개")
                
                all_results[ticker] = result
                
            except FileNotFoundError:
                print(f"   ❌ 파일 없음")
                all_results[ticker] = {'error': 'No file'}
        
        # 저장
        with open('data/universal_extraction_results.json', 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*80}")
        print("✅ 저장: data/universal_extraction_results.json")
        print("="*80)
        
        return all_results


if __name__ == "__main__":
    extractor = UniversalDataExtractor()
    
    STOCKS = ['AAPL', 'META', 'NVDA', 'AMZN', 'TSLA']
    
    results = extractor.extract_all_stocks(STOCKS)
    
    # 샘플 출력
    print(f"\n{'='*80}")
    print("📋 샘플 추출 결과 (AAPL)")
    print('='*80)
    
    if 'AAPL' in results:
        aapl = results['AAPL']
        
        for category, findings in aapl['extracted'].items():
            if findings:
                print(f"\n🔍 {category}:")
                for i, finding in enumerate(findings[:3], 1):  # 처음 3개만
                    context = finding.get('context', finding.get('matched', ''))
                    print(f"   {i}. {context[:150]}...")
    
    print(f"\n{'='*80}")
    print("💡 이제 우리는:")
    print("="*80)
    print("  ✅ 경쟁사 언급 자동 추출")
    print("  ✅ 신제품 로드맵 발견")
    print("  ✅ 공급망 리스크 구체화")
    print("  ✅ 경영진 전망 파악")
    print("  ✅ 지정학 영향 추적")
    print()
    print("→ 이것이 진짜 차별화! 🚀")
    print("="*80)

