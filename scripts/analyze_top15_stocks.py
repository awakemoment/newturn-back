"""
Top 15 종목 정성적 분석
Claude가 직접 분석!

실행: python scripts/analyze_top15_stocks.py
"""
import json
from datetime import datetime


class QualitativeAnalyzer:
    """정성적 분석 엔진 (Claude 직접 분석)"""
    
    def __init__(self):
        self.analyses = {}
    
    def analyze_all(self):
        """15개 종목 모두 분석"""
        
        stocks = [
            'AAPL',  # 이미 완료
            'MSFT',
            'GOOGL',
            'AMZN',
            'NVDA',
            'META',
            'TSLA',
            'JPM',
            'V',
            'JNJ',
            'WMT',
            'PG',
            'XOM',
            'CVX',
            'KO',
        ]
        
        for ticker in stocks:
            print(f"\n{'='*70}")
            print(f"🔍 Analyzing {ticker}...")
            print('='*70)
            
            analysis = self.analyze_stock(ticker)
            self.analyses[ticker] = analysis
            
            # 저장
            self.save_analysis(ticker, analysis)
            
            print(f"✅ {ticker} 분석 완료!")
        
        return self.analyses
    
    def analyze_stock(self, ticker):
        """개별 종목 분석"""
        
        # 종목별로 다른 분석 함수 호출
        if ticker == 'AAPL':
            return self.analyze_aapl()
        elif ticker == 'MSFT':
            return self.analyze_msft()
        elif ticker == 'GOOGL':
            return self.analyze_googl()
        elif ticker == 'AMZN':
            return self.analyze_amzn()
        elif ticker == 'NVDA':
            return self.analyze_nvda()
        elif ticker == 'META':
            return self.analyze_meta()
        elif ticker == 'TSLA':
            return self.analyze_tsla()
        elif ticker == 'JPM':
            return self.analyze_jpm()
        elif ticker == 'V':
            return self.analyze_visa()
        elif ticker == 'JNJ':
            return self.analyze_jnj()
        elif ticker == 'WMT':
            return self.analyze_walmart()
        elif ticker == 'PG':
            return self.analyze_pg()
        elif ticker == 'XOM':
            return self.analyze_exxon()
        elif ticker == 'CVX':
            return self.analyze_chevron()
        elif ticker == 'KO':
            return self.analyze_coke()
    
    def analyze_msft(self):
        """Microsoft 분석"""
        return {
            'ticker': 'MSFT',
            'company_name': 'Microsoft Corporation',
            'analyzed_at': datetime.now().isoformat(),
            
            'business_model': {
                'model_type': 'Enterprise Software + Cloud + Gaming',
                'description': 'Microsoft는 Windows, Office(Microsoft 365), Azure 클라우드, LinkedIn, Gaming(Xbox)을 통해 기업과 소비자 시장에서 수익을 창출합니다.',
                'revenue_streams': [
                    {'stream': 'Azure Cloud', 'characteristics': '고성장(30%+), 고마진, 반복 수익'},
                    {'stream': 'Office 365', 'characteristics': '구독 모델, 안정적, 기업 필수'},
                    {'stream': 'Windows', 'characteristics': '라이선스, OEM, 성숙 시장'},
                    {'stream': 'LinkedIn', 'characteristics': '광고+프리미엄, 네트워크 효과'},
                    {'stream': 'Gaming', 'characteristics': 'Xbox, Game Pass, Activision 인수'},
                ],
                'understandability_score': 8,
                'reason': '기업용 소프트웨어와 클라우드. 누구나 Windows, Office 알지만 Azure는 다소 복잡.'
            },
            
            'competitive_advantages': {
                'moat_strength': '매우 강함 (Wide Moat)',
                'moat_sustainability': 9,
                'moat_factors': [
                    {'type': 'Enterprise Lock-in', 'strength': 10, 'description': '전 세계 기업의 90%가 Windows/Office 사용. 전환 비용 극도로 높음.'},
                    {'type': 'Network Effects', 'strength': 9, 'description': 'Office 협업, LinkedIn 네트워크, Azure 개발자 생태계'},
                    {'type': 'Switching Costs', 'strength': 10, 'description': '수백만 문서, 업무 프로세스, 직원 교육 투자'},
                    {'type': 'Brand Power', 'strength': 8, 'description': '기업 신뢰도 최고. "안전한 선택"'},
                    {'type': 'Scale', 'strength': 9, 'description': '클라우드 인프라 투자 경쟁사 압도'},
                ],
                'moat_durability': '10년+',
                'moat_widening': True,
            },
            
            'risks': {
                'overall_risk_level': '낮음',
                'risk_score': 35,
                'top_3_risks': [
                    'Cloud 경쟁 심화 (AWS, Google Cloud)',
                    'AI 전환 리스크 (Google Bard, OpenAI 의존)',
                    '규제 리스크 (반독점, Activision 인수)'
                ]
            },
            
            'investment_appeal': {
                'overall_score': 90,
                'grade': 'A+',
                'strengths': [
                    'Cloud 고성장 (Azure 30%+)',
                    '구독 모델 (안정적 반복 수익)',
                    'AI 선도 (OpenAI 투자, Copilot)',
                    '막강한 현금 창출',
                    '다각화된 수익원'
                ],
                'sustainability_score': 8,
            },
            
            'mate_assessments': {
                'benjamin': {
                    'score': 80,
                    'assessment': 'BUY',
                    'verdict': '재무 안전성 최고. FCF 강력. 배당 꾸준. 밸류에이션 다소 높지만 품질 고려 시 합리적.',
                    'recommendation': '장기 보유 추천. Core 포지션.'
                },
                'fisher': {
                    'score': 95,
                    'assessment': 'STRONG BUY',
                    'verdict': 'Cloud 고성장. AI 선도. 경영진 우수(Satya Nadella). R&D 적극적. 완벽한 성장주.',
                    'recommendation': '최우선 매수. 10년 보유.'
                },
                'greenblatt': {
                    'score': 95,
                    'assessment': 'TOP PICK',
                    'verdict': 'ROIC 최상급. 자본 효율 완벽. 마법공식 상위권.',
                    'recommendation': 'Must-own 종목.'
                },
                'daily': {
                    'score': 85,
                    'assessment': 'BUY',
                    'verdict': '회사에서 매일 쓰는 Office, Teams. 클라우드는 좀 복잡하지만 필수 인프라.',
                    'recommendation': '안정적 보유.'
                }
            }
        }
    
    def analyze_googl(self):
        """Google (Alphabet) 분석"""
        return {
            'ticker': 'GOOGL',
            'company_name': 'Alphabet Inc.',
            'analyzed_at': datetime.now().isoformat(),
            
            'business_model': {
                'model_type': 'Advertising + Cloud + Others',
                'description': 'Google Search, YouTube 광고가 핵심. Google Cloud 성장 중. Waymo(자율주행), Verily(헬스케어) 등 기타 사업.',
                'revenue_streams': [
                    {'stream': 'Search Ads', 'characteristics': '압도적 점유율, 초고마진'},
                    {'stream': 'YouTube Ads', 'characteristics': '동영상 광고 1위, 고성장'},
                    {'stream': 'Google Cloud', 'characteristics': '3위(AWS, Azure 다음), 빠른 성장'},
                    {'stream': 'Play Store', 'characteristics': '앱 수수료, Android 생태계'},
                ],
                'understandability_score': 9,
                'reason': '검색, YouTube 누구나 매일 사용. 비즈니스 모델 명확.'
            },
            
            'competitive_advantages': {
                'moat_strength': '매우 강함 (Wide Moat)',
                'moat_sustainability': 10,
                'moat_factors': [
                    {'type': 'Network Effects', 'strength': 10, 'description': '검색 많을수록 데이터 많음 → 검색 품질 상승 → 사용자 증가 (선순환)'},
                    {'type': 'Brand Power', 'strength': 10, 'description': '"구글링" = 검색의 대명사. 브랜드 인지도 완벽.'},
                    {'type': 'Data Moat', 'strength': 10, 'description': '20년+ 축적 검색 데이터. 경쟁사 따라잡기 불가능.'},
                    {'type': 'Scale', 'strength': 10, 'description': '검색 시장 점유율 90%+. 광고주 플랫폼 필수.'},
                ],
                'moat_durability': '10년+',
                'moat_widening': True,
            },
            
            'risks': {
                'overall_risk_level': '중간',
                'risk_score': 45,
                'top_3_risks': [
                    'AI 검색 전환 (ChatGPT, Bing AI)',
                    '광고 의존도 (80%+)',
                    '규제 리스크 (반독점, EU, 검색 독점)'
                ]
            },
            
            'investment_appeal': {
                'overall_score': 88,
                'grade': 'A+',
                'strengths': [
                    '검색 독점 (90%+ 점유율)',
                    'YouTube 1위',
                    '초고마진 (60%+)',
                    'AI 기술 선도 (DeepMind, Gemini)',
                    '막강한 현금 보유'
                ],
                'sustainability_score': 9,
            },
            
            'mate_assessments': {
                'benjamin': {
                    'score': 82,
                    'assessment': 'BUY',
                    'verdict': '현금 $100B+, 부채 거의 없음. FCF 강력. PER 25 정도로 합리적.',
                    'recommendation': '안전한 투자.'
                },
                'fisher': {
                    'score': 88,
                    'assessment': 'STRONG BUY',
                    'verdict': 'AI 기술 최강. Cloud 고성장. 경영진 우수. 장기 성장 확실.',
                    'recommendation': '핵심 보유.'
                },
                'greenblatt': {
                    'score': 100,
                    'assessment': 'PERFECT',
                    'verdict': 'ROIC 압도적. 이익 수익률 최상. 마법공식 1위급.',
                    'recommendation': 'Must-own!'
                },
                'daily': {
                    'score': 100,
                    'assessment': 'MUST OWN',
                    'verdict': '매일 쓰는 Google 검색, YouTube, Gmail, Maps. 삶의 필수품.',
                    'recommendation': '포트폴리오 핵심 (20%+)'
                }
            }
        }
    
    def analyze_amzn(self):
        """Amazon 분석"""
        return {
            'ticker': 'AMZN',
            'company_name': 'Amazon.com Inc.',
            'analyzed_at': datetime.now().isoformat(),
            
            'business_model': {
                'model_type': 'E-commerce + Cloud + Advertising',
                'description': '이커머스(아마존닷컴)와 AWS(클라우드)가 양대 축. 광고 사업 급성장 중.',
                'revenue_streams': [
                    {'stream': 'E-commerce', 'characteristics': '저마진(5%), 거대 규모, 프라임 멤버십'},
                    {'stream': 'AWS', 'characteristics': '초고마진(30%), 클라우드 1위, 핵심 수익원'},
                    {'stream': 'Advertising', 'characteristics': '고성장(20%+), 고마진, 신성장 동력'},
                    {'stream': 'Prime', 'characteristics': '구독(연회비), 락인 효과'},
                ],
                'understandability_score': 9,
                'reason': '아마존 쇼핑 누구나 알고 사용. AWS는 좀 복잡하지만 클라우드 컴퓨팅.'
            },
            
            'competitive_advantages': {
                'moat_strength': '매우 강함 (Wide Moat)',
                'moat_sustainability': 9,
                'moat_factors': [
                    {'type': 'Scale', 'strength': 10, 'description': '물류 네트워크 세계 최대. 2일 배송 인프라. 경쟁사 불가능.'},
                    {'type': 'Network Effects', 'strength': 9, 'description': '판매자 많음 → 상품 다양 → 고객 증가 → 판매자 증가 (선순환)'},
                    {'type': 'Prime Ecosystem', 'strength': 9, 'description': 'Prime 멤버 2억명+. Video, Music, 배송 혜택. 락인 강력.'},
                    {'type': 'AWS Leadership', 'strength': 8, 'description': 'AWS 클라우드 1위(32%). 기술력, 생태계 최강.'},
                ],
                'moat_durability': '10년+',
                'moat_widening': True,
            },
            
            'risks': {
                'overall_risk_level': '중간',
                'risk_score': 50,
                'top_3_risks': [
                    'AWS 경쟁 심화 (MSFT, Google)',
                    'E-commerce 저마진',
                    '규제 리스크 (반독점, 노동 이슈)'
                ]
            },
            
            'investment_appeal': {
                'overall_score': 85,
                'grade': 'A',
                'strengths': [
                    'AWS 압도적 리더 (32% 점유율)',
                    '거대 물류 네트워크',
                    'Prime 2억 멤버',
                    '광고 고성장',
                    '혁신 문화'
                ],
                'sustainability_score': 7,
            },
            
            'mate_assessments': {
                'benjamin': {
                    'score': 65,
                    'assessment': 'HOLD',
                    'verdict': 'E-commerce 저마진 우려. AWS는 우수. 전체적으로 안전마진 부족.',
                    'recommendation': '하락 시 검토.'
                },
                'fisher': {
                    'score': 92,
                    'assessment': 'STRONG BUY',
                    'verdict': '혁신 능력 최고. AWS, 광고 고성장. 장기 전망 탁월.',
                    'recommendation': '10년 보유.'
                },
                'greenblatt': {
                    'score': 75,
                    'assessment': 'BUY',
                    'verdict': 'AWS는 ROIC 높지만 E-commerce가 희석. 종합 적당.',
                    'recommendation': '적정가 이하 시 매수.'
                },
                'daily': {
                    'score': 98,
                    'assessment': 'MUST OWN',
                    'verdict': '매일 쓰는 아마존. 배송 빠르고 편리. 생활 필수.',
                    'recommendation': '핵심 보유.'
                }
            }
        }
    
    def save_analysis(self, ticker, analysis):
        """분석 결과 저장"""
        filename = f'data/qual_{ticker}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"   💾 Saved to {filename}")


# 실행
if __name__ == "__main__":
    print("="*70)
    print("🚀 Top 15 종목 정성적 분석 시작")
    print("="*70)
    
    analyzer = QualitativeAnalyzer()
    
    # 우선 빅테크 3개만 (MSFT, GOOGL, AMZN)
    print("\n📊 Phase 1: 빅테크 3종 (MSFT, GOOGL, AMZN)")
    
    for ticker in ['MSFT', 'GOOGL', 'AMZN']:
        analysis = analyzer.analyze_stock(ticker)
        analyzer.save_analysis(ticker, analysis)
        
        # 요약 출력
        print(f"\n{'='*70}")
        print(f"✅ {ticker} - {analysis['company_name']}")
        print(f"{'='*70}")
        print(f"종합 점수: {analysis['investment_appeal']['overall_score']}/100")
        print(f"등급: {analysis['investment_appeal']['grade']}")
        print(f"\n메이트 평가:")
        for mate, data in analysis['mate_assessments'].items():
            print(f"  {mate}: {data['score']}점 - {data['assessment']}")
    
    print(f"\n{'='*70}")
    print("🎉 Phase 1 완료!")
    print("="*70)
    print("\n다음: NVDA, META, TSLA, JPM, V, JNJ, WMT, PG, XOM, CVX, KO")
    print("→ 나머지는 요청 시 추가 분석!")


