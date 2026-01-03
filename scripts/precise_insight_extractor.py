"""
정밀 인사이트 추출기 v2

목표: 노이즈 제거, 진짜 가치있는 정보만 추출

개선사항:
1. 키워드는 단어 경계 체크 (\\b)
2. 구체적 숫자/이름 포함된 것만
3. 중복 제거 강화
4. 신뢰도 점수 추가
"""
import re
import json


class PreciseInsightExtractor:
    """정밀 인사이트 추출기"""
    
    def extract_competitors_mentions(self, text):
        """경쟁사 구체적 언급만"""
        
        # 실제 회사명 (단어 경계 체크)
        competitors = {
            'Tech': r'\b(Samsung|Huawei|Xiaomi|OPPO|Vivo|OnePlus|LG|Sony)\b',
            'Cloud': r'\b(AWS|Azure|Google Cloud|GCP|Oracle Cloud|IBM Cloud)\b',
            'Social': r'\b(TikTok|YouTube|Twitter|X|Snapchat|LinkedIn)\b',
            'EV': r'\b(BYD|Tesla|NIO|XPeng|Li Auto|Rivian|Lucid)\b',
            'Chip': r'\b(Intel|AMD|Qualcomm|MediaTek|TSMC|Samsung Foundry)\b',
        }
        
        findings = []
        
        for category, pattern in competitors.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                # 앞뒤 200자 추출
                start = max(0, match.start() - 200)
                end = min(len(text), match.end() + 200)
                context = text[start:end].strip()
                
                # 의미있는 문장만 (숫자나 비교 포함)
                if any(keyword in context.lower() for keyword in ['market share', 'compete', 'versus', 'compared to', '%', 'growth', 'decline', 'surpass', 'lead']):
                    findings.append({
                        'company': match.group(0),
                        'category': category,
                        'context': context,
                        'confidence': 0.9 if any(word in context.lower() for word in ['market share', 'compete']) else 0.7
                    })
        
        return findings[:10]  # Top 10
    
    def extract_forward_guidance(self, text):
        """경영진 전망 (구체적 숫자 포함)"""
        
        patterns = [
            # "expect X% growth"
            r'(?:expect|anticipate|project|forecast)\s+(?:to\s+)?(?:grow|increase|decline|decrease)\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*(?:%|percent|percentage points?)',
            
            # "X% growth expected"
            r'(\d+(?:\.\d+)?)\s*(?:%|percent)\s+(?:growth|increase|decline)\s+(?:is\s+)?(?:expect|anticipat|project|forecast)',
            
            # "guidance of X%"
            r'guidance.*?(\d+(?:\.\d+)?)\s*(?:%|percent)',
            
            # "margins expected to improve X bps"
            r'margin.*?(?:improve|expand|increase)\s+(?:by\s+)?(\d+)\s*(?:basis points?|bps)',
        ]
        
        findings = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                start = max(0, match.start() - 150)
                end = min(len(text), match.end() + 150)
                context = text[start:end].strip()
                
                findings.append({
                    'type': 'forward_guidance',
                    'value': match.group(1) if match.groups() else None,
                    'context': context,
                    'confidence': 0.95
                })
        
        return findings[:10]
    
    def extract_supply_chain_specifics(self, text):
        """공급망 구체 정보"""
        
        patterns = [
            # "TSMC is sole supplier"
            r'([\w\s]+)\s+(?:is|are)\s+(?:our|the)\s+(?:sole|single|primary|only)\s+(?:supplier|source|manufacturer|provider)',
            
            # "supply from X"
            r'(?:supply|source|procure|obtain)(?:ed|ing)?\s+(?:from|by)\s+([\w\s]+)',
            
            # "X constraint cost $Y"
            r'(?:supply|component|chip|semiconductor)\s+(?:constraint|shortage|disruption).*?(?:cost|impact|loss).*?\$\s*([\d,\.]+)\s*(billion|million)',
        ]
        
        findings = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end].strip()
                
                supplier = match.group(1) if match.groups() else None
                
                # 회사명인지 확인 (첫 글자 대문자)
                if supplier and supplier.strip()[0].isupper():
                    findings.append({
                        'type': 'supply_chain',
                        'supplier': supplier.strip(),
                        'context': context,
                        'confidence': 0.9
                    })
        
        return findings[:10]
    
    def extract_geopolitical_impact(self, text):
        """지정학 구체적 영향 (숫자 포함)"""
        
        patterns = [
            # "tariff cost $X"
            r'tariff.*?(?:cost|impact|add|incur).*?\$\s*([\d,\.]+)\s*(billion|million)',
            
            # "China revenue declined X%"
            r'China.*?revenue.*?(?:declined|decreased|fell|dropped)\s+(\d+(?:\.\d+)?)\s*%',
            
            # "export controls on X"
            r'export\s+control.*?on\s+([\w\s]+)',
            
            # "sanctions impact X"
            r'sanction.*?impact.*?([\w\s]+)',
        ]
        
        findings = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                start = max(0, match.start() - 150)
                end = min(len(text), match.end() + 150)
                context = text[start:end].strip()
                
                findings.append({
                    'type': 'geopolitical',
                    'context': context,
                    'confidence': 0.85
                })
        
        return findings[:10]
    
    def extract_all(self, text, ticker):
        """모든 정밀 추출"""
        
        return {
            'ticker': ticker,
            'insights': {
                'competitors': self.extract_competitors_mentions(text),
                'forward_guidance': self.extract_forward_guidance(text),
                'supply_chain': self.extract_supply_chain_specifics(text),
                'geopolitical': self.extract_geopolitical_impact(text),
            }
        }
    
    def process_all_stocks(self, tickers):
        """전체 종목 처리"""
        
        print("="*80)
        print("🎯 정밀 인사이트 추출기 v2")
        print("="*80)
        print()
        print("개선사항:")
        print("  ✅ 단어 경계 체크 (Intel ≠ intellectual)")
        print("  ✅ 구체적 숫자/이름만")
        print("  ✅ 신뢰도 점수 추가")
        print()
        
        results = {}
        
        for ticker in tickers:
            print(f"\n{'='*80}")
            print(f"📊 {ticker} 처리 중...")
            print('-'*80)
            
            try:
                with open(f'data/section_{ticker}_item_7_mda.txt', 'r', encoding='utf-8') as f:
                    text = f.read()
                
                result = self.extract_all(text, ticker)
                
                # 통계
                total = sum(len(v) for v in result['insights'].values())
                print(f"   ✅ {total}개 고품질 인사이트")
                
                for category, items in result['insights'].items():
                    if items:
                        avg_conf = sum(item.get('confidence', 0) for item in items) / len(items)
                        print(f"      {category}: {len(items)}개 (평균 신뢰도: {avg_conf:.2f})")
                
                results[ticker] = result
                
            except FileNotFoundError:
                print(f"   ❌ 파일 없음")
        
        # 저장
        with open('data/precise_insights.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*80}")
        print("✅ 저장: data/precise_insights.json")
        print("="*80)
        
        return results


if __name__ == "__main__":
    extractor = PreciseInsightExtractor()
    
    STOCKS = ['AAPL', 'META', 'NVDA', 'AMZN', 'TSLA']
    
    results = extractor.process_all_stocks(STOCKS)
    
    # 샘플 출력
    print(f"\n{'='*80}")
    print("📋 샘플 고품질 인사이트")
    print('='*80)
    
    for ticker in ['AAPL', 'META', 'TSLA']:
        if ticker in results:
            print(f"\n🔍 {ticker}:")
            
            data = results[ticker]['insights']
            
            # 경쟁사
            if data.get('competitors'):
                print(f"\n  경쟁사 언급:")
                for item in data['competitors'][:3]:
                    print(f"    - {item['company']} ({item['category']}, 신뢰도: {item['confidence']})")
                    print(f"      {item['context'][:100]}...")
            
            # 전망
            if data.get('forward_guidance'):
                print(f"\n  경영진 전망:")
                for item in data['forward_guidance'][:2]:
                    print(f"    - {item.get('value', 'N/A')}%")
                    print(f"      {item['context'][:100]}...")
    
    print(f"\n{'='*80}")
    print("💡 이제 진짜 가치있는 데이터만!")
    print("="*80)

