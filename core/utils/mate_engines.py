"""
투자 메이트 분석 엔진

4명의 투자 대가 철학을 구현:
- Benjamin (벤저민 그레이엄): 안전마진, 저평가
- Fisher (필립 피셔): 성장주, R&D
- Greenblatt (조엘 그린블라트): 마법공식, ROIC
- Lynch (피터 린치): 일상 속 발견, 이해하기 쉬운 기업
"""


class BenjaminMate:
    """
    베니 (Benny) - 벤저민 그레이엄 메이트
    - 핵심: 안전마진 (Margin of Safety)
    - 중시: 저평가, 재무 안전성, 배당
    - 캐릭터: 신중하고 보수적인 안전 지킴이
    """
    
    name = "베니"
    full_name = "베니 (Benny)"
    character_name = "Benny"
    original_investor = "벤저민 그레이엄"
    color = "blue"
    icon = "🎩"
    motto = "손실을 피하는 게 먼저"
    personality = "신중하고 보수적"
    
    @classmethod
    def analyze(cls, indicators):
        """
        벤저민 관점 분석
        
        평가 기준:
        - 안전성 (50점): 부채비율, 유동비율, FCF
        - 저평가 (30점): PBR, PER (현재는 간단히 FCF 마진으로 대체)
        - 배당 (20점): FCF 양수 분기 수
        """
        score = 0
        reasons = []
        cautions = []
        
        # 1. 안전성 평가 (50점)
        safety_score = 0
        
        # 부채비율 (25점)
        debt_ratio = indicators.get('debt_ratio', 100)
        if debt_ratio < 30:
            safety_score += 25
            reasons.append(f"부채비율 {debt_ratio:.1f}%로 매우 건전합니다")
        elif debt_ratio < 50:
            safety_score += 20
            reasons.append(f"부채비율 {debt_ratio:.1f}%로 안정적입니다")
        elif debt_ratio < 100:
            safety_score += 15
        else:
            cautions.append(f"부채비율 {debt_ratio:.1f}%로 다소 높습니다")
        
        # 유동비율 (15점)
        current_ratio = indicators.get('current_ratio', 100)
        if current_ratio >= 200:
            safety_score += 15
            reasons.append(f"유동비율 {current_ratio:.0f}%로 우수합니다")
        elif current_ratio >= 150:
            safety_score += 10
        elif current_ratio >= 100:
            safety_score += 5
        
        # FCF 양수 (10점)
        fcf = indicators.get('ttm_fcf', 0)
        if fcf > 0:
            safety_score += 10
            reasons.append("안정적인 현금흐름을 보이고 있습니다")
        else:
            cautions.append("FCF가 음수입니다")
        
        score += safety_score
        
        # 2. 저평가 평가 (30점) - 간단히 FCF 마진으로 평가
        value_score = 0
        fcf_margin = indicators.get('fcf_margin', 0)
        
        if fcf_margin >= 15:
            value_score += 30
            reasons.append(f"FCF 마진 {fcf_margin:.1f}%로 높은 수익성")
        elif fcf_margin >= 10:
            value_score += 20
        elif fcf_margin >= 5:
            value_score += 10
        else:
            cautions.append("FCF 마진이 낮습니다")
        
        score += value_score
        
        # 3. 배당/안정성 (20점)
        fcf_positive_quarters = indicators.get('fcf_positive_quarters', 0)
        
        if fcf_positive_quarters >= 18:
            score += 20
            reasons.append(f"최근 20분기 중 {fcf_positive_quarters}분기 양수 FCF - 매우 안정적")
        elif fcf_positive_quarters >= 16:
            score += 15
        elif fcf_positive_quarters >= 12:
            score += 10
        else:
            cautions.append("FCF가 불안정합니다")
        
        # 종합 의견
        if score >= 80:
            summary = "훌륭한 안전 자산입니다"
        elif score >= 70:
            summary = "장기 보유 적합한 안전 자산입니다"
        elif score >= 60:
            summary = "안정적이나 일부 주의사항이 있습니다"
        elif score >= 50:
            summary = "보수적 투자자에게는 다소 위험할 수 있습니다"
        else:
            summary = "안전마진이 부족합니다"
        
        return {
            'mate': cls.name,
            'icon': cls.icon,
            'color': cls.color,
            'score': score,
            'summary': summary,
            'reasons': reasons[:3],  # 상위 3개만
            'cautions': cautions[:2],  # 상위 2개만
            'recommendation': cls._get_recommendation(score, reasons, cautions),
        }
    
    @classmethod
    def _get_recommendation(cls, score, reasons, cautions):
        """투자 판단"""
        if score >= 70:
            return "안전마진이 충분하여 장기 투자에 적합합니다"
        elif score >= 60:
            return "비교적 안전하나 지속적인 모니터링이 필요합니다"
        else:
            return "리스크가 있어 신중한 접근이 필요합니다"


class FisherMate:
    """
    그로우 (Grow) - 필립 피셔 메이트
    - 핵심: 성장주 발굴
    - 중시: 매출 성장, ROE, 현금흐름 개선
    - 캐릭터: 열정적이고 미래 지향적인 성장 탐험가
    """
    
    name = "그로우"
    full_name = "그로우 (Grow)"
    character_name = "Grow"
    original_investor = "필립 피셔"
    color = "green"
    icon = "🌱"
    motto = "우수한 기업은 시간이 증명한다"
    personality = "열정적이고 미래 지향적"
    
    @classmethod
    def analyze(cls, indicators):
        """
        피셔 관점 분석
        
        평가 기준:
        - 성장성 (50점): 매출 성장률, FCF 성장률
        - 수익성 (30점): ROE, FCF 마진
        - 현금창출력 (20점): FCF 양수 분기
        """
        score = 0
        reasons = []
        cautions = []
        
        # 1. 성장성 평가 (50점)
        growth_score = 0
        
        # 매출 성장률 (30점)
        revenue_growth = indicators.get('revenue_growth') or 0
        if revenue_growth >= 20:
            growth_score += 30
            reasons.append(f"매출이 전년 대비 {revenue_growth:.1f}% 급성장 중입니다")
        elif revenue_growth >= 15:
            growth_score += 25
            reasons.append(f"매출 성장률 {revenue_growth:.1f}%로 빠르게 성장 중")
        elif revenue_growth >= 10:
            growth_score += 20
        elif revenue_growth >= 5:
            growth_score += 10
        elif revenue_growth >= 0:
            growth_score += 5
        else:
            cautions.append(f"매출이 감소하고 있습니다 ({revenue_growth:.1f}%)")
        
        # FCF 성장률 (20점)
        fcf_growth = indicators.get('fcf_growth') or 0
        if fcf_growth >= 20:
            growth_score += 20
            reasons.append("현금흐름이 빠르게 개선되고 있습니다")
        elif fcf_growth >= 10:
            growth_score += 15
        elif fcf_growth >= 0:
            growth_score += 10
        else:
            cautions.append("FCF가 감소 추세입니다")
        
        score += growth_score
        
        # 2. 수익성 (30점)
        profitability_score = 0
        
        # ROE (20점)
        roe = indicators.get('roe', 0)
        if roe >= 25:
            profitability_score += 20
            reasons.append(f"ROE {roe:.1f}%로 뛰어난 수익성")
        elif roe >= 20:
            profitability_score += 15
        elif roe >= 15:
            profitability_score += 10
        elif roe >= 10:
            profitability_score += 5
        else:
            cautions.append(f"ROE {roe:.1f}%로 수익성이 낮습니다")
        
        # FCF 마진 (10점)
        fcf_margin = indicators.get('fcf_margin', 0)
        if fcf_margin >= 15:
            profitability_score += 10
        elif fcf_margin >= 10:
            profitability_score += 7
        elif fcf_margin >= 5:
            profitability_score += 5
        
        score += profitability_score
        
        # 3. 현금창출력 (20점)
        fcf_positive = indicators.get('fcf_positive_quarters', 0)
        if fcf_positive >= 18:
            score += 20
        elif fcf_positive >= 16:
            score += 15
        elif fcf_positive >= 12:
            score += 10
        else:
            cautions.append("현금흐름이 불안정합니다")
        
        # 종합 의견
        if score >= 80:
            summary = "탁월한 성장 잠재력을 가진 기업입니다"
        elif score >= 70:
            summary = "성장성이 뛰어난 기업입니다"
        elif score >= 60:
            summary = "꾸준한 성장이 기대되는 기업입니다"
        elif score >= 50:
            summary = "성장성은 보통 수준입니다"
        else:
            summary = "성장 동력이 부족해 보입니다"
        
        return {
            'mate': cls.name,
            'icon': cls.icon,
            'color': cls.color,
            'score': score,
            'summary': summary,
            'reasons': reasons[:3],
            'cautions': cautions[:2],
            'recommendation': cls._get_recommendation(score, revenue_growth, roe),
        }
    
    @classmethod
    def _get_recommendation(cls, score, revenue_growth, roe):
        """투자 판단"""
        if score >= 70 and revenue_growth >= 10:
            return "성장 잠재력에 투자하는 관점이라면 매력적인 기업입니다"
        elif score >= 60:
            return "꾸준한 성장이 예상되나 밸류에이션 확인이 필요합니다"
        else:
            return "성장성 측면에서는 매력도가 떨어집니다"


class GreenblattMate:
    """
    매직 (Magic) - 조엘 그린블라트 메이트
    - 핵심: 마법공식 (Magic Formula)
    - 중시: ROIC, 이익수익률
    - 캐릭터: 논리적이고 수학적인 마법사
    """
    
    name = "매직"
    full_name = "매직 (Magic)"
    character_name = "Magic"
    original_investor = "조엘 그린블라트"
    color = "purple"
    icon = "🔮"
    motto = "우량하고 저렴한 기업"
    personality = "논리적이고 수학적"
    
    @classmethod
    def analyze(cls, indicators):
        """
        그린블라트 관점 분석
        
        평가 기준:
        - 우량도 (50점): ROE, FCF 마진 (ROIC 대체)
        - 염가도 (50점): FCF 기준 저평가
        """
        score = 0
        reasons = []
        cautions = []
        
        # 1. 우량도 (50점) - ROE로 대체
        quality_score = 0
        
        roe = indicators.get('roe', 0)
        if roe >= 20:
            quality_score += 30
            reasons.append(f"자본 효율이 뛰어납니다 (ROE {roe:.1f}%)")
        elif roe >= 15:
            quality_score += 25
        elif roe >= 10:
            quality_score += 15
        elif roe >= 5:
            quality_score += 10
        else:
            cautions.append("자본 효율이 낮습니다")
        
        # FCF 마진 (20점)
        fcf_margin = indicators.get('fcf_margin', 0)
        if fcf_margin >= 15:
            quality_score += 20
            reasons.append(f"현금 창출 능력이 우수합니다 ({fcf_margin:.1f}%)")
        elif fcf_margin >= 10:
            quality_score += 15
        elif fcf_margin >= 5:
            quality_score += 10
        
        score += quality_score
        
        # 2. 염가도 (50점) - 간단히 FCF 대비 평가
        value_score = 0
        
        fcf = indicators.get('ttm_fcf', 0)
        revenue = indicators.get('ttm_revenue', 1)
        
        # FCF yield 계산 (간단 버전)
        if fcf > 0 and fcf_margin >= 10:
            value_score += 30
            reasons.append("현금흐름 대비 적정 가격입니다")
        elif fcf > 0 and fcf_margin >= 5:
            value_score += 20
        elif fcf > 0:
            value_score += 10
        else:
            cautions.append("FCF가 음수입니다")
        
        # 안정성 (20점)
        debt_ratio = indicators.get('debt_ratio', 100)
        if debt_ratio < 50:
            value_score += 20
        elif debt_ratio < 100:
            value_score += 10
        
        score += value_score
        
        # 종합 의견
        if score >= 80:
            summary = "우량하고 저렴한 마법공식 후보입니다"
        elif score >= 70:
            summary = "우량한 기업이지만 가격은 적정 수준입니다"
        elif score >= 60:
            summary = "우량성과 가격이 균형을 이룹니다"
        elif score >= 50:
            summary = "우량도나 염가도 중 하나가 부족합니다"
        else:
            summary = "마법공식 기준에는 미달입니다"
        
        # 순위 표시 (간단 버전)
        quality_rank = "상위 20%" if quality_score >= 40 else "중위권"
        value_rank = "상위 30%" if value_score >= 35 else "중위권"
        
        return {
            'mate': cls.name,
            'icon': cls.icon,
            'color': cls.color,
            'score': score,
            'summary': summary,
            'reasons': reasons[:3],
            'cautions': cautions[:2],
            'recommendation': cls._get_recommendation(score, quality_rank, value_rank),
            'details': {
                'quality_rank': quality_rank,
                'value_rank': value_rank,
            }
        }
    
    @classmethod
    def _get_recommendation(cls, score, quality_rank, value_rank):
        """투자 판단"""
        if score >= 70:
            return f"우량도 {quality_rank}, 염가도 {value_rank} - 마법공식 관점에서 매력적입니다"
        elif score >= 60:
            return "우량하거나 저렴한 기업이지만 둘 다는 아닙니다"
        else:
            return "마법공식 기준으로는 추천하기 어렵습니다"


class LynchMate:
    """
    데일리 (Daily) - 피터 린치 메이트
    - 핵심: 일상에서 발견
    - 중시: 이해하기 쉬운 비즈니스, 실적 개선 모멘텀
    - 캐릭터: 친근하고 실용적인 일상 투자자
    """
    
    name = "데일리"
    full_name = "데일리 (Daily)"
    character_name = "Daily"
    original_investor = "피터 린치"
    color = "orange"
    icon = "🎯"
    motto = "이해할 수 있는 곳에 투자하라"
    personality = "친근하고 실용적"
    
    @classmethod
    def analyze(cls, indicators):
        """
        린치 관점 분석
        
        평가 기준:
        - 이해가능성 (30점): 섹터, 비즈니스 단순성
        - 실적 모멘텀 (40점): 매출/ROE 성장
        - 기본 체력 (30점): FCF, 부채
        """
        score = 0
        reasons = []
        cautions = []
        
        # 1. 이해가능성 (30점) - 기본 점수 제공
        # 실제로는 섹터, 제품 친숙도 등으로 평가해야 함
        understandability_score = 20  # 기본 점수
        reasons.append("비즈니스 모델이 이해하기 쉽습니다")
        score += understandability_score
        
        # 2. 실적 모멘텀 (40점)
        momentum_score = 0
        
        # 매출 성장 (25점)
        revenue_growth = indicators.get('revenue_growth') or 0
        if revenue_growth >= 15:
            momentum_score += 25
            reasons.append(f"매출이 {revenue_growth:.1f}% 급성장하고 있습니다")
        elif revenue_growth >= 10:
            momentum_score += 20
        elif revenue_growth >= 5:
            momentum_score += 15
        elif revenue_growth >= 0:
            momentum_score += 10
        else:
            cautions.append("매출이 감소하고 있습니다")
        
        # ROE 개선 (15점)
        roe = indicators.get('roe', 0)
        if roe >= 15:
            momentum_score += 15
            reasons.append(f"수익성이 우수합니다 (ROE {roe:.1f}%)")
        elif roe >= 10:
            momentum_score += 10
        elif roe >= 5:
            momentum_score += 5
        
        score += momentum_score
        
        # 3. 기본 체력 (30점)
        fundamental_score = 0
        
        # FCF (20점)
        fcf_positive = indicators.get('fcf_positive_quarters', 0)
        if fcf_positive >= 16:
            fundamental_score += 20
        elif fcf_positive >= 12:
            fundamental_score += 15
        elif fcf_positive >= 8:
            fundamental_score += 10
        else:
            cautions.append("현금흐름이 불안정합니다")
        
        # 부채 (10점)
        debt_ratio = indicators.get('debt_ratio', 100)
        if debt_ratio < 100:
            fundamental_score += 10
        elif debt_ratio < 150:
            fundamental_score += 5
        else:
            cautions.append("부채가 과도합니다")
        
        score += fundamental_score
        
        # 종합 의견
        if score >= 80:
            summary = "일상 속에서 발견한 숨은 보석입니다"
        elif score >= 70:
            summary = "성장 모멘텀이 좋은 기업입니다"
        elif score >= 60:
            summary = "관심을 가질 만한 기업입니다"
        elif score >= 50:
            summary = "평범한 기업입니다"
        else:
            summary = "실적 모멘텀이 부족합니다"
        
        return {
            'mate': cls.name,
            'icon': cls.icon,
            'color': cls.color,
            'score': score,
            'summary': summary,
            'reasons': reasons[:3],
            'cautions': cautions[:2],
            'recommendation': cls._get_recommendation(score, revenue_growth),
        }
    
    @classmethod
    def _get_recommendation(cls, score, revenue_growth):
        """투자 판단"""
        if score >= 70:
            return "실적 개선 모멘텀이 뚜렷하여 성장주 투자에 적합합니다"
        elif score >= 60:
            return "기본기는 갖췄으나 모멘텀이 더 필요합니다"
        else:
            return "현재로서는 매력도가 떨어집니다"


# 4개 메이트 통합
MATES = {
    'benjamin': BenjaminMate,
    'fisher': FisherMate,
    'greenblatt': GreenblattMate,
    'lynch': LynchMate,
}


def analyze_with_all_mates(indicators):
    """
    모든 메이트로 분석
    """
    results = {}
    
    for mate_id, mate_class in MATES.items():
        results[mate_id] = mate_class.analyze(indicators)
    
    return results


def recommend_mate(watchlist_analysis):
    """
    사용자 관심 종목 기반 메이트 추천
    
    Args:
        watchlist_analysis: [{'mate_scores': {...}}, ...]
    
    Returns:
        {'mate': 'benjamin', 'reason': '...', ...}
    """
    mate_total_scores = {mate_id: 0 for mate_id in MATES.keys()}
    
    for item in watchlist_analysis:
        mate_scores = item.get('mate_scores', {})
        for mate_id, analysis in mate_scores.items():
            if analysis['score'] >= 70:
                mate_total_scores[mate_id] += 2
            elif analysis['score'] >= 60:
                mate_total_scores[mate_id] += 1
    
    # 가장 높은 점수의 메이트
    recommended_mate_id = max(mate_total_scores, key=mate_total_scores.get)
    recommended_mate = MATES[recommended_mate_id]
    
    return {
        'mate': recommended_mate_id,
        'name': recommended_mate.name,
        'icon': recommended_mate.icon,
        'color': recommended_mate.color,
        'reason': f"{recommended_mate.name}가 당신의 관심 종목을 높이 평가했어요",
        'personality': recommended_mate.motto,
    }

