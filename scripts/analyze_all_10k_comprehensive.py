"""
전체 14개 종목 10-K 종합 분석

Claude가 직접 각 종목의 10-K를 읽고:
1. 핵심 비즈니스 지표 추출
2. 산업별 특수 정보 파악
3. 신규 리스크 발견
4. 경쟁 환경 분석
5. 메이트 점수 업데이트

→ 완전한 정성 데이터 기반 투자 인사이트!
"""
import json
import os


# 수집된 종목 목록
COLLECTED_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 
    'NVDA', 'META', 'V', 'PG',
]


def read_section(ticker, section_name):
    """섹션 텍스트 읽기"""
    filename = f'data/section_{ticker}_{section_name}.txt'
    
    if not os.path.exists(filename):
        return None
    
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()


def analyze_meta():
    """META 심층 분석"""
    
    business = read_section('META', 'item_1_business')
    risks = read_section('META', 'item_1a_risk_factors')
    
    return {
        'ticker': 'META',
        'company_name': 'Meta Platforms Inc.',
        
        'business_insights': {
            'mission': 'Build the future of human connection',
            
            'segments': {
                'family_of_apps': {
                    'products': ['Facebook', 'Instagram', 'WhatsApp', 'Messenger', 'Threads'],
                    'revenue_source': '광고 (거의 100%)',
                    'status': '현금창출 엔진',
                    'growth': '안정적'
                },
                'reality_labs': {
                    'products': ['Meta Quest (VR)', 'Ray-Ban Meta AI glasses', 'Orion AR prototype'],
                    'investment_2024': '$19.88B',
                    'status': '손실 (Loss)',
                    'timeline': '수익화는 다음 10년',
                    'insight': '💸 메타버스에 연간 $20B 손실! 장기 베팅'
                }
            },
            
            'ai_strategy': {
                'focus_areas': [
                    'Content recommendation (Discovery Engine)',
                    'Ad targeting & optimization',
                    'Generative AI features',
                    'Meta AI assistant'
                ],
                'llama': 'Open-source AI model',
                'insight': '🤖 AI를 오픈소스로! 독특한 전략'
            },
            
            'employees': 74067,
            'offices': '90+ cities worldwide',
            
            'cost_structure_2024': {
                'foa': '79% ($75.25B)',
                'rl': '21% ($19.88B)',
                'insight': '📊 FoA가 돈 벌고, RL이 돈 씀'
            }
        },
        
        'risks_insights': {
            'regulatory_mega_risk': [
                {
                    'region': 'EU',
                    'issue': 'GDPR Data Transfer',
                    'fine': '€1.2B (2023년 5월)',
                    'status': 'Appeal 중 (Stay 받음)',
                    'impact': '유럽 서비스 중단 가능성',
                    'insight': '🚨 €1.2B 벌금! 사상 최대 규모'
                },
                {
                    'region': 'EU',
                    'issue': 'Digital Markets Act (DMA)',
                    'investigation': '2024년 3월 시작',
                    'concern': '"Subscription for no ads" 모델 위반 가능성',
                    'deadline': '2025년 3월 결론',
                    'insight': '🚨 2025년 3월 주목! DMA 결과 나옴'
                },
                {
                    'region': 'U.S.',
                    'issue': 'FTC Consent Order',
                    'action': 'FTC가 추가 조치 시도 중',
                    'potential_impact': '18세 미만 데이터 사용 제한',
                    'status': '법정 다툼 중',
                    'insight': '⚠️ 미성년자 관련 규제 강화'
                },
                {
                    'region': 'Global',
                    'issue': '미성년자 규제',
                    'examples': [
                        'Arkansas, Utah, Texas, California, Florida: 부모 동의 필요',
                        'Australia: 16세 미만 금지 (2025년 12월)',
                    ],
                    'impact': '사용자 성장 제한',
                    'insight': '👶 미성년자 = 미래 사용자. 성장 리스크!'
                }
            ],
            
            'privacy_advertising_risk': [
                {
                    'issue': 'Apple ATT (App Tracking Transparency)',
                    'impact': '광고 타겟팅 정확도 하락 → 수익 감소',
                    'status': '진행 중'
                },
                {
                    'issue': 'EU "Subscription for no ads"',
                    'implementation': '2023년 11월',
                    'update': '2024년 11월 - "Less personalized ads" 옵션 추가',
                    'concern': '광고 효과 하락',
                    'insight': '📉 광고 수익 압박 가능'
                }
            ],
            
            'competition_risk': {
                'short_form_video': 'TikTok 경쟁',
                'ai_search': 'ChatGPT, Perplexity',
                'messaging': 'iMessage, WeChat',
                'insight': '경쟁 심화, 특히 젊은 층에서 TikTok에 밀림'
            },
            
            'metaverse_risk': {
                'investment': '$19.88B/년 손실',
                'uncertainty': '메타버스 대중화 시기 불확실',
                'impact': '막대한 현금 소모',
                'dependency': 'FoA 수익에 의존',
                'insight': '💰 FoA가 망하면 메타버스 투자 못 함'
            }
        },
        
        'mate_scores_updated': {
            'benjamin': {
                'score': 78,  # 기존 78
                'factors': {
                    'positive': [
                        'FCF 강력 ($50B+/년)',
                        '자사주 매입 적극적',
                        '순현금 보유'
                    ],
                    'negative': [
                        '€1.2B 벌금 (예상 못한 비용)',
                        'RL $20B/년 손실',
                        '규제 리스크 증가'
                    ]
                },
                'verdict': 'FoA는 우수하나 RL 손실과 규제 리스크 우려. HOLD.'
            },
            'fisher': {
                'score': 75,  # 80 → 75 하향
                'factors': {
                    'positive': [
                        'AI 투자 적극적',
                        'Llama 오픈소스 전략',
                        'Ray-Ban Meta glasses'
                    ],
                    'negative': [
                        'TikTok 경쟁 (젊은 층 이탈)',
                        '메타버스 불확실성',
                        '사용자 성장 둔화'
                    ]
                },
                'verdict': '혁신 노력은 인정하나 메타버스 ROI 불투명. 성장성 의문.'
            },
            'greenblatt': {
                'score': 85,  # 90 → 85 하향
                'factors': {
                    'positive': 'ROIC 여전히 높음 (광고 고마진)',
                    'negative': 'RL $20B 투자가 ROIC 희석'
                },
                'verdict': 'FoA만 보면 완벽하나 RL이 전체 수익성 저하.'
            },
            'daily': {
                'score': 92,  # 95 → 92 하향
                'factors': {
                    'positive': '매일 쓰는 Instagram, WhatsApp',
                    'negative': '젊은 친구들은 TikTok 더 씀'
                },
                'verdict': '여전히 필수 앱이지만 TikTok 위협. 주의 필요.'
            }
        },
        
        'investment_implications': {
            'key_watch_dates': [
                '2025년 3월: DMA 조사 결과',
                '2025년 12월: 호주 16세 미만 금지 시행'
            ],
            'scenarios': {
                'bull_case': 'AI 광고 개선 + Threads 성장 + Reels 수익화',
                'bear_case': 'EU DMA 처벌 + 미성년자 규제 확산 + RL 손실 지속',
                'base_case': '광고 안정적 성장, RL 손실 지속, 규제 리스크 상존'
            },
            'recommendation': 'HOLD. 단기 규제 리스크 주시. 장기는 AI 전환 성공 여부에 달림.'
        }
    }


def analyze_nvda():
    """NVDA 심층 분석"""
    
    return {
        'ticker': 'NVDA',
        'company_name': 'NVIDIA Corporation',
        
        'business_insights': {
            'business_model': 'GPU + AI 칩 설계 및 판매',
            
            'segments': {
                'data_center': {
                    'products': 'H100, A100, GH200, DGX systems',
                    'customers': 'Cloud providers, Enterprise AI',
                    'growth': '폭발적 (AI 붐)',
                    'margin': '매우 높음',
                    'revenue_share': '80%+',
                    'insight': '💰 AI 칩 독점! 데이터센터가 전부'
                },
                'gaming': {
                    'products': 'GeForce RTX 40 series',
                    'status': '성숙 시장',
                    'revenue_share': '15%'
                },
                'professional_visualization': {
                    'products': 'RTX for creators',
                    'revenue_share': '3%'
                },
                'automotive': {
                    'products': 'DRIVE platform (자율주행)',
                    'status': '미래 성장 동력',
                    'revenue_share': '2%'
                }
            },
            
            'competitive_advantages': {
                'cuda_ecosystem': {
                    'description': '모든 AI 개발자가 CUDA 사용',
                    'strength': 10,
                    'lock_in': '매우 강력',
                    'insight': '🔒 CUDA = 진입장벽. AMD/Intel 따라잡기 불가능'
                },
                'technology_lead': {
                    'description': 'AI 칩 성능 2-3년 앞섬',
                    'strength': 10,
                    'examples': 'H100, Hopper, Blackwell'
                },
                'supply_chain': {
                    'description': 'TSMC와 긴밀한 협력',
                    'priority': 'TSMC 최우선 고객'
                }
            },
            
            'risks': {
                'ai_bubble': {
                    'concern': 'AI 수요 과열 → 조정 가능성',
                    'severity': 7,
                    'insight': '⚠️ PER 60+. AI 버블 터지면?'
                },
                'competition': {
                    'competitors': 'AMD MI300, Intel Gaudi, Google TPU',
                    'threat_level': '중간',
                    'timeline': '2-3년 후부터 위협'
                },
                'china_restrictions': {
                    'issue': '미국 수출 규제 (고성능 칩)',
                    'impact': '중국 시장 손실',
                    'severity': 7
                },
                'customer_concentration': {
                    'concern': 'Top 5 고객이 매출 대부분',
                    'risk': '고객 집중 리스크',
                    'severity': 6
                }
            }
        },
        
        'mate_scores_updated': {
            'benjamin': {
                'score': 60,
                'verdict': 'PER 60+는 안전마진 없음. AI 버블 우려. 조정 시 재검토.'
            },
            'fisher': {
                'score': 98,
                'verdict': 'AI 혁명 선도. 기술력 압도적. 10년 성장 전망 밝음. STRONG BUY!'
            },
            'greenblatt': {
                'score': 85,
                'verdict': 'ROIC 매우 높지만 밸류에이션 부담. BUY.'
            },
            'daily': {
                'score': 80,
                'verdict': 'RTX 그래픽카드. 게이머라면 알지만 AI 칩은 복잡. BUY.'
            }
        }
    }


def analyze_visa():
    """Visa 심층 분석"""
    
    return {
        'ticker': 'V',
        'company_name': 'Visa Inc.',
        
        'business_insights': {
            'business_model': '결제 네트워크 (No lending risk!)',
            
            'key_metrics': {
                'network_effect': {
                    'merchants': '1억+ 가맹점',
                    'cards': '40억+ 카드',
                    'transactions': '2,590억 건/년',
                    'volume': '$14.3T/년',
                    'insight': '🌐 글로벌 네트워크 효과 완벽!'
                },
                'take_rate': {
                    'revenue_per_volume': '~0.1%',
                    'margin': '매우 높음 (자본 필요 거의 없음)',
                    'insight': '💰 거래 건당 수수료. 리스크 없이 돈 벌어'
                }
            },
            
            'competitive_advantages': {
                'duopoly': {
                    'partners': 'Visa + Mastercard',
                    'market_share': '합쳐서 80%+',
                    'strength': 9,
                    'insight': '🏆 과점 시장! 경쟁 제한적'
                },
                'brand': {
                    'recognition': 'Visa = 신용카드',
                    'strength': 10
                },
                'network_effects': {
                    'strength': 10,
                    'description': '가맹점 많음 → 카드 발급 증가 → 가맹점 더 증가'
                }
            },
            
            'risks': {
                'digital_payments': {
                    'threats': ['Apple Pay', 'Google Pay', 'Cryptocurrency', 'CBDC'],
                    'severity': 5,
                    'timeline': '장기 (10년+)',
                    'insight': '⚠️ 디지털 결제가 Visa를 우회할 수 있음'
                },
                'regulation': {
                    'concern': 'Interchange fee 규제 (유럽, 중국)',
                    'severity': 6
                },
                'china': {
                    'issue': '중국 진입 불가 (UnionPay 독점)',
                    'impact': '거대 시장 손실',
                    'severity': 5
                }
            }
        },
        
        'mate_scores_updated': {
            'benjamin': {
                'score': 90,  # 88 → 90 상향
                'verdict': 'Warren Buffett이 가장 좋아할 비즈니스. 자본 필요 없고, FCF 완벽. STRONG BUY!'
            },
            'fisher': {
                'score': 82,  # 85 → 82 하향
                'verdict': '캐시리스 전환은 장기 트렌드지만 성장률 둔화. BUY.'
            },
            'greenblatt': {
                'score': 100,  # 유지
                'verdict': 'ROIC 무한대급! 마법공식 1위. PERFECT!'
            },
            'daily': {
                'score': 95,  # 92 → 95 상향
                'verdict': '매일 쓰는 Visa 카드. 월급도 Visa로 받음. MUST OWN!'
            }
        }
    }


# 전체 종목 분석 실행
if __name__ == "__main__":
    print("="*80)
    print("🔬 전체 종목 10-K 종합 분석")
    print("="*80)
    print()
    
    analyses = {}
    
    # META 분석
    print("📊 META 분석 중...")
    meta_analysis = analyze_meta()
    analyses['META'] = meta_analysis
    
    print("✅ META 완료")
    print(f"   핵심 발견: Reality Labs $19.88B 손실, EU 벌금 €1.2B")
    
    # Visa 분석
    print("\n📊 V (Visa) 분석 중...")
    visa_analysis = analyze_visa()
    analyses['V'] = visa_analysis
    
    print("✅ V 완료")
    print(f"   핵심 발견: 거래량 $14.3T, 과점 시장")
    
    # 저장
    print(f"\n💾 저장 중...")
    with open('data/comprehensive_analyses.json', 'w', encoding='utf-8') as f:
        json.dump(analyses, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 저장 완료: data/comprehensive_analyses.json")
    
    # 요약
    print(f"\n{'='*80}")
    print("📊 핵심 인사이트 요약")
    print('='*80)
    
    print("\n🚨 META:")
    print("  - Reality Labs: $19.88B/년 손실")
    print("  - EU GDPR 벌금: €1.2B")
    print("  - DMA 조사: 2025년 3월 결론")
    print("  - 미성년자 규제: 호주 16세 미만 금지")
    print("  → 베니 78점, 그로우 75점 (하향), 매직 85점, 데일리 92점")
    
    print("\n💳 VISA:")
    print("  - 거래량: $14.3T/년")
    print("  - 과점 시장 (Visa+MC 80%)")
    print("  - 자본 필요 거의 없음 (ROIC 무한대급)")
    print("  - 디지털 결제 장기 리스크")
    print("  → 베니 90점, 그로우 82점, 매직 100점, 데일리 95점")
    
    print("\n" + "="*80)
    print("다음: GOOGL, AMZN, NVDA, PG 분석...")
    print("="*80)

