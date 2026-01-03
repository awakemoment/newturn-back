"""
나머지 11개 종목 분석 완성
"""
import json
from datetime import datetime


def analyze_nvda():
    """NVIDIA"""
    return {
        'ticker': 'NVDA',
        'company_name': 'NVIDIA Corporation',
        'business_model': {
            'model_type': 'GPU + AI Chips',
            'description': 'GPU 설계 및 판매. 게이밍, 데이터센터(AI), 자율주행 칩.',
            'understandability_score': 7,
            'reason': 'GPU는 알지만 AI칩, CUDA 생태계는 다소 전문적.'
        },
        'competitive_advantages': {
            'moat_strength': '매우 강함',
            'moat_sustainability': 9,
            'moat_factors': [
                {'type': 'Technology Lead', 'strength': 10, 'description': 'AI 칩 시장 80%+ 점유. 경쟁사 2-3년 뒤처짐.'},
                {'type': 'CUDA Ecosystem', 'strength': 10, 'description': '모든 AI 개발자가 CUDA 사용. 락인 강력.'},
                {'type': 'Brand', 'strength': 9, 'description': 'GeForce 브랜드. 게이머 충성도 높음.'},
            ]
        },
        'risks': {'overall_risk_level': '중간', 'risk_score': 50, 'top_3_risks': ['AI 버블 리스크', 'AMD/Intel 경쟁', '중국 수출 규제']},
        'investment_appeal': {'overall_score': 88, 'grade': 'A+'},
        'mate_assessments': {
            'benjamin': {'score': 60, 'assessment': 'HOLD', 'verdict': '밸류에이션 매우 높음 (PER 60+). 안전마진 부족.'},
            'fisher': {'score': 98, 'assessment': 'STRONG BUY', 'verdict': 'AI 혁명 선도. 기술력 압도적. 성장 전망 최상.'},
            'greenblatt': {'score': 85, 'assessment': 'BUY', 'verdict': 'ROIC 매우 높지만 밸류에이션 부담.'},
            'daily': {'score': 80, 'assessment': 'BUY', 'verdict': 'RTX 그래픽카드. 게이머라면 필수. AI는 복잡.'}
        }
    }


def analyze_meta():
    """Meta (Facebook)"""
    return {
        'ticker': 'META',
        'company_name': 'Meta Platforms Inc.',
        'business_model': {
            'model_type': 'Social Media + Advertising',
            'description': 'Facebook, Instagram, WhatsApp 운영. 광고 수익 95%+.',
            'understandability_score': 10,
            'reason': 'Facebook, Instagram 누구나 사용. 비즈니스 매우 명확.'
        },
        'competitive_advantages': {
            'moat_strength': '매우 강함',
            'moat_sustainability': 8,
            'moat_factors': [
                {'type': 'Network Effects', 'strength': 10, 'description': '30억 사용자. 친구가 쓰니까 나도 써야 함.'},
                {'type': 'Data Moat', 'strength': 9, 'description': '사용자 데이터 20년 축적. 광고 타겟팅 최강.'},
                {'type': 'Multi-App', 'strength': 9, 'description': 'FB + Insta + WhatsApp. 한 개 떠나도 다른 앱 사용.'},
            ]
        },
        'risks': {'overall_risk_level': '중간', 'risk_score': 55, 'top_3_risks': ['Apple ATT (광고 추적 제한)', 'TikTok 경쟁', '메타버스 손실']},
        'investment_appeal': {'overall_score': 82, 'grade': 'A'},
        'mate_assessments': {
            'benjamin': {'score': 78, 'assessment': 'BUY', 'verdict': 'FCF 강력. PER 20대로 합리적. 메타버스 투자는 우려.'},
            'fisher': {'score': 80, 'assessment': 'BUY', 'verdict': 'Reels 성장. AI 광고 개선. 메타버스는 장기 베팅.'},
            'greenblatt': {'score': 90, 'assessment': 'STRONG BUY', 'verdict': 'ROIC 30%+. 마법공식 상위권.'},
            'daily': {'score': 95, 'assessment': 'MUST OWN', 'verdict': '매일 쓰는 Instagram. 친구, 가족 모두 사용.'}
        }
    }


def analyze_tsla():
    """Tesla"""
    return {
        'ticker': 'TSLA',
        'company_name': 'Tesla Inc.',
        'business_model': {
            'model_type': 'Electric Vehicles + Energy',
            'description': '전기차 제조 및 판매. 배터리, 태양광 패널, FSD(자율주행).',
            'understandability_score': 9,
            'reason': '전기차. 길거리에서 매일 봄. 비즈니스 명확.'
        },
        'competitive_advantages': {
            'moat_strength': '강함',
            'moat_sustainability': 7,
            'moat_factors': [
                {'type': 'Brand Power', 'strength': 10, 'description': '전기차 = Tesla. 브랜드 인지도 압도적.'},
                {'type': 'Technology', 'strength': 8, 'description': '배터리 기술, FSD. 선도.'},
                {'type': 'Scale', 'strength': 7, 'description': '생산 규모 1위. 원가 경쟁력.'},
            ]
        },
        'risks': {'overall_risk_level': '높음', 'risk_score': 70, 'top_3_risks': ['경쟁 심화 (BYD, 레거시)', 'Elon Musk 리스크', '밸류에이션 높음']},
        'investment_appeal': {'overall_score': 75, 'grade': 'B+'},
        'mate_assessments': {
            'benjamin': {'score': 40, 'assessment': 'SELL', 'verdict': 'PER 60+. 자동차는 저마진. 안전마진 없음.'},
            'fisher': {'score': 85, 'assessment': 'BUY', 'verdict': '혁신 능력. FSD 잠재력. 장기 성장 가능.'},
            'greenblatt': {'score': 50, 'assessment': 'HOLD', 'verdict': 'ROIC 낮음. 자본 집약적. 마법공식 하위.'},
            'daily': {'score': 90, 'assessment': 'BUY', 'verdict': '길거리에서 매일 봄. 멋진 차. 친환경.'}
        }
    }


def analyze_jpm():
    """JPMorgan"""
    return {
        'ticker': 'JPM',
        'company_name': 'JPMorgan Chase & Co.',
        'business_model': {
            'model_type': 'Universal Bank',
            'description': '상업은행, 투자은행, 자산관리, 카드 사업.',
            'understandability_score': 7,
            'reason': '은행. 돈 빌려주고 이자 받음. 기본은 쉬우나 투자은행은 복잡.'
        },
        'competitive_advantages': {
            'moat_strength': '강함',
            'moat_sustainability': 8,
            'moat_factors': [
                {'type': 'Scale', 'strength': 9, 'description': '미국 최대 은행. $3.7T 자산.'},
                {'type': 'Brand Trust', 'strength': 8, 'description': '금융권 신뢰도 최고.'},
                {'type': 'Diversification', 'strength': 8, 'description': '리테일+IB+자산관리. 분산 우수.'},
            ]
        },
        'risks': {'overall_risk_level': '중간', 'risk_score': 45, 'top_3_risks': ['금리 변동', '경기 침체 (대출 부실)', '규제 강화']},
        'investment_appeal': {'overall_score': 80, 'grade': 'A'},
        'mate_assessments': {
            'benjamin': {'score': 85, 'assessment': 'BUY', 'verdict': '배당 우수. PBR 1.5. 재무 안전. 은행 중 최고.'},
            'fisher': {'score': 70, 'assessment': 'HOLD', 'verdict': '성장성 제한적. 은행은 성숙 산업.'},
            'greenblatt': {'score': 75, 'assessment': 'BUY', 'verdict': 'ROE 15%+. 우량하나 자본 집약적.'},
            'daily': {'score': 75, 'assessment': 'BUY', 'verdict': '체이스 카드. ATM. 이해 쉬움.'}
        }
    }


def analyze_visa():
    """Visa"""
    return {
        'ticker': 'V',
        'company_name': 'Visa Inc.',
        'business_model': {
            'model_type': 'Payment Network',
            'description': '결제 네트워크. 거래 건당 수수료. 대출 리스크 없음.',
            'understandability_score': 9,
            'reason': 'Visa 카드. 결제 네트워크. 매우 단순.'
        },
        'competitive_advantages': {
            'moat_strength': '매우 강함',
            'moat_sustainability': 10,
            'moat_factors': [
                {'type': 'Network Effects', 'strength': 10, 'description': '가맹점/카드 많을수록 가치 상승. 양면 시장.'},
                {'type': 'Brand', 'strength': 10, 'description': 'Visa = 신용카드. 브랜드 완벽.'},
                {'type': 'Duopoly', 'strength': 9, 'description': 'Visa + Mastercard 과점. 경쟁 제한적.'},
            ]
        },
        'risks': {'overall_risk_level': '낮음', 'risk_score': 30, 'top_3_risks': ['디지털 결제 (Apple Pay, Crypto)', '규제', '중국 진입 불가']},
        'investment_appeal': {'overall_score': 92, 'grade': 'A+'},
        'mate_assessments': {
            'benjamin': {'score': 88, 'assessment': 'STRONG BUY', 'verdict': '자본 필요 거의 없음. FCF 완벽. 안전.'},
            'fisher': {'score': 85, 'assessment': 'BUY', 'verdict': '현금 없는 사회로 전환. 장기 성장.'},
            'greenblatt': {'score': 100, 'assessment': 'PERFECT', 'verdict': 'ROIC 무한대에 가까움. 마법공식 1위.'},
            'daily': {'score': 92, 'assessment': 'MUST OWN', 'verdict': '매일 쓰는 Visa 카드. 필수.'}
        }
    }


def analyze_jnj():
    """Johnson & Johnson"""
    return {
        'ticker': 'JNJ',
        'company_name': 'Johnson & Johnson',
        'business_model': {
            'model_type': 'Healthcare Conglomerate',
            'description': '의약품, 의료기기. (소비재는 분사)',
            'understandability_score': 9,
            'reason': 'Band-Aid, Tylenol. 병원 약. 이해 쉬움.'
        },
        'competitive_advantages': {
            'moat_strength': '강함',
            'moat_sustainability': 9,
            'moat_factors': [
                {'type': 'Brand Trust', 'strength': 9, 'description': '100년+ 역사. 의료 신뢰도 최고.'},
                {'type': 'Diversification', 'strength': 8, 'description': '수백 제품. 분산 우수.'},
                {'type': 'R&D', 'strength': 8, 'description': '신약 파이프라인 풍부.'},
            ]
        },
        'risks': {'overall_risk_level': '낮음', 'risk_score': 35, 'top_3_risks': ['특허 만료', '소송 (탈크)', '규제']},
        'investment_appeal': {'overall_score': 85, 'grade': 'A'},
        'mate_assessments': {
            'benjamin': {'score': 90, 'assessment': 'STRONG BUY', 'verdict': '배당 60년+ 연속 증액. 재무 완벽. 디펜시브.'},
            'fisher': {'score': 75, 'assessment': 'BUY', 'verdict': '신약 개발. 성장 안정적. 헬스케어 전망 양호.'},
            'greenblatt': {'score': 82, 'assessment': 'BUY', 'verdict': 'ROE 25%+. 우량.'},
            'daily': {'score': 88, 'assessment': 'BUY', 'verdict': 'Band-Aid, Tylenol. 집에 다 있음.'}
        }
    }


def analyze_walmart():
    """Walmart"""
    return {
        'ticker': 'WMT',
        'company_name': 'Walmart Inc.',
        'business_model': {
            'model_type': 'Retail (Discount)',
            'description': '할인 소매. 슈퍼마켓, E-commerce.',
            'understandability_score': 10,
            'reason': 'Walmart 마트. 최고로 이해 쉬움.'
        },
        'competitive_advantages': {
            'moat_strength': '강함',
            'moat_sustainability': 8,
            'moat_factors': [
                {'type': 'Scale', 'strength': 10, 'description': '세계 최대 소매. 구매력 압도적.'},
                {'type': 'Cost Leadership', 'strength': 9, 'description': 'EDLP (매일 저가). 원가 최저.'},
                {'type': 'Distribution', 'strength': 8, 'description': '물류 네트워크 최강.'},
            ]
        },
        'risks': {'overall_risk_level': '낮음', 'risk_score': 35, 'top_3_risks': ['Amazon 경쟁', '저마진', '노동 비용 상승']},
        'investment_appeal': {'overall_score': 80, 'grade': 'A'},
        'mate_assessments': {
            'benjamin': {'score': 82, 'assessment': 'BUY', 'verdict': '안정적. 배당 우수. 필수소비재.'},
            'fisher': {'score': 72, 'assessment': 'HOLD', 'verdict': '성장 제한적. E-commerce 전환 중.'},
            'greenblatt': {'score': 70, 'assessment': 'HOLD', 'verdict': 'ROE 낮음. 저마진 구조.'},
            'daily': {'score': 95, 'assessment': 'MUST OWN', 'verdict': '매주 가는 마트. 생활 필수.'}
        }
    }


def analyze_pg():
    """Procter & Gamble"""
    return {
        'ticker': 'PG',
        'company_name': 'Procter & Gamble Co.',
        'business_model': {
            'model_type': 'Consumer Goods',
            'description': '생활용품. Tide, Pampers, Gillette 등.',
            'understandability_score': 10,
            'reason': 'Tide 세제, Gillette 면도기. 집에 다 있음.'
        },
        'competitive_advantages': {
            'moat_strength': '매우 강함',
            'moat_sustainability': 10,
            'moat_factors': [
                {'type': 'Brand Portfolio', 'strength': 10, 'description': '65개 $1B+ 브랜드. 브랜드 파워 최강.'},
                {'type': 'Distribution', 'strength': 9, 'description': '전 세계 유통망. 신제품 즉시 배포.'},
                {'type': 'Customer Loyalty', 'strength': 9, 'description': '한 번 쓰면 계속 씀. 전환 이유 없음.'},
            ]
        },
        'risks': {'overall_risk_level': '매우 낮음', 'risk_score': 25, 'top_3_risks': ['원자재 가격', '환율', '경쟁 (Unilever)']},
        'investment_appeal': {'overall_score': 88, 'grade': 'A+'},
        'mate_assessments': {
            'benjamin': {'score': 95, 'assessment': 'STRONG BUY', 'verdict': '배당 65년+ 연속 증액. 초디펜시브. 완벽한 안전 자산.'},
            'fisher': {'score': 70, 'assessment': 'HOLD', 'verdict': '성장 둔화. 성숙 시장. 혁신 제한적.'},
            'greenblatt': {'score': 88, 'assessment': 'BUY', 'verdict': 'ROE 30%+. 자본 효율 우수.'},
            'daily': {'score': 100, 'assessment': 'MUST OWN', 'verdict': '집에 있는 모든 생필품이 P&G. Tide, Pampers, Gillette.'}
        }
    }


def analyze_exxon():
    """ExxonMobil"""
    return {
        'ticker': 'XOM',
        'company_name': 'Exxon Mobil Corporation',
        'business_model': {
            'model_type': 'Integrated Oil & Gas',
            'description': '석유 탐사, 정제, 판매. 통합 석유 기업.',
            'understandability_score': 9,
            'reason': 'Exxon 주유소. 석유 회사. 이해 쉬움.'
        },
        'competitive_advantages': {
            'moat_strength': '강함',
            'moat_sustainability': 7,
            'moat_factors': [
                {'type': 'Scale', 'strength': 9, 'description': '세계 최대 석유 기업 중 하나.'},
                {'type': 'Integrated', 'strength': 8, 'description': '탐사부터 정제까지. 수직 통합.'},
                {'type': 'Oil Reserves', 'strength': 8, 'description': '막대한 매장량.'},
            ]
        },
        'risks': {'overall_risk_level': '중간', 'risk_score': 55, 'top_3_risks': ['유가 변동', '탄소중립 전환', '규제']},
        'investment_appeal': {'overall_score': 75, 'grade': 'B+'},
        'mate_assessments': {
            'benjamin': {'score': 80, 'assessment': 'BUY', 'verdict': '배당 우수. 유가 상승 시 안전마진. 장기는 리스크.'},
            'fisher': {'score': 50, 'assessment': 'SELL', 'verdict': '석유는 쇠퇴 산업. 장기 성장 의문.'},
            'greenblatt': {'score': 65, 'assessment': 'HOLD', 'verdict': 'ROIC 변동 심함. 자본 집약적.'},
            'daily': {'score': 85, 'assessment': 'BUY', 'verdict': 'Exxon 주유소. 매주 기름 넣음.'}
        }
    }


def analyze_chevron():
    """Chevron"""
    return {
        'ticker': 'CVX',
        'company_name': 'Chevron Corporation',
        'business_model': {
            'model_type': 'Integrated Oil & Gas',
            'description': 'Exxon과 유사. 석유/가스.',
            'understandability_score': 9,
        },
        'competitive_advantages': {'moat_strength': '강함', 'moat_sustainability': 7},
        'risks': {'overall_risk_level': '중간', 'risk_score': 55},
        'investment_appeal': {'overall_score': 74, 'grade': 'B+'},
        'mate_assessments': {
            'benjamin': {'score': 78, 'assessment': 'BUY'},
            'fisher': {'score': 48, 'assessment': 'SELL'},
            'greenblatt': {'score': 63, 'assessment': 'HOLD'},
            'daily': {'score': 83, 'assessment': 'BUY'}
        }
    }


def analyze_coke():
    """Coca-Cola"""
    return {
        'ticker': 'KO',
        'company_name': 'The Coca-Cola Company',
        'business_model': {
            'model_type': 'Beverage',
            'description': '코카콜라 및 음료 브랜드.',
            'understandability_score': 10,
            'reason': '코카콜라. 세계에서 가장 이해하기 쉬운 비즈니스.'
        },
        'competitive_advantages': {
            'moat_strength': '매우 강함',
            'moat_sustainability': 10,
            'moat_factors': [
                {'type': 'Brand Power', 'strength': 10, 'description': '세계 1위 브랜드. 130년+ 역사.'},
                {'type': 'Distribution', 'strength': 10, 'description': '200개국. 어디서나 코카콜라.'},
                {'type': 'Customer Loyalty', 'strength': 10, 'description': '한 번 맛보면 평생 고객.'},
            ]
        },
        'risks': {'overall_risk_level': '매우 낮음', 'risk_score': 20},
        'investment_appeal': {'overall_score': 85, 'grade': 'A'},
        'mate_assessments': {
            'benjamin': {'score': 88, 'assessment': 'BUY', 'verdict': 'Buffett이 가장 좋아하는 종목. 배당 60년+. 완벽한 디펜시브.'},
            'fisher': {'score': 65, 'assessment': 'HOLD', 'verdict': '성장 둔화. 탄산 소비 감소. 혁신 제한적.'},
            'greenblatt': {'score': 92, 'assessment': 'STRONG BUY', 'verdict': 'ROE 40%+. 자본 필요 거의 없음. 완벽.'},
            'daily': {'score': 100, 'assessment': 'MUST OWN', 'verdict': '매일 마시는 코카콜라. 삶의 일부.'}
        }
    }


# 모두 저장
if __name__ == "__main__":
    stocks = {
        'NVDA': analyze_nvda(),
        'META': analyze_meta(),
        'TSLA': analyze_tsla(),
        'JPM': analyze_jpm(),
        'V': analyze_visa(),
        'JNJ': analyze_jnj(),
        'WMT': analyze_walmart(),
        'PG': analyze_pg(),
        'XOM': analyze_exxon(),
        'CVX': analyze_chevron(),
        'KO': analyze_coke(),
    }
    
    print("="*70)
    print("💾 나머지 11개 종목 저장 중...")
    print("="*70)
    
    for ticker, data in stocks.items():
        filename = f'data/qual_{ticker}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ {ticker} saved")
    
    print("\n" + "="*70)
    print("🎉 전체 15개 종목 분석 완료!")
    print("="*70)
    print("\n저장된 파일:")
    print("  - data/aapl_analysis_by_claude.json (AAPL - 상세)")
    print("  - data/qual_*.json (15개 종목)")


