"""
적정가격 계산 엔진

다양한 밸류에이션 방법:
1. DCF (Discounted Cash Flow)
2. Graham Number (벤저민 그레이엄 공식)
3. Category PER (동종업계 PER)
4. PBR 기반 (자산 가치)
"""
from decimal import Decimal
from typing import Dict, Optional


class ValuationEngine:
    """적정가격 계산 엔진"""
    
    @staticmethod
    def calculate_dcf(fcf: float, growth_rate: float = 0.05, discount_rate: float = 0.10, 
                      terminal_growth: float = 0.03, years: int = 10, shares_outstanding: int = 1000000000) -> Decimal:
        """
        DCF (Discounted Cash Flow) 모델
        
        Args:
            fcf: 현재 FCF (TTM)
            growth_rate: 성장률 (기본 5%)
            discount_rate: 할인율 (기본 10%)
            terminal_growth: 영구 성장률 (기본 3%)
            years: 예측 기간 (기본 10년)
            shares_outstanding: 발행 주식 수
        
        Returns:
            주당 적정가격
        """
        if fcf <= 0:
            return Decimal('0')
        
        # 1. 명시적 예측 기간 FCF 현재가치
        pv_fcf = 0
        for year in range(1, years + 1):
            future_fcf = fcf * ((1 + growth_rate) ** year)
            pv = future_fcf / ((1 + discount_rate) ** year)
            pv_fcf += pv
        
        # 2. 영구 가치 (Terminal Value)
        terminal_fcf = fcf * ((1 + growth_rate) ** years) * (1 + terminal_growth)
        terminal_value = terminal_fcf / (discount_rate - terminal_growth)
        pv_terminal = terminal_value / ((1 + discount_rate) ** years)
        
        # 3. 기업 가치
        enterprise_value = pv_fcf + pv_terminal
        
        # 4. 주당 가치
        price_per_share = enterprise_value / shares_outstanding
        
        return Decimal(str(round(price_per_share, 2)))
    
    @staticmethod
    def calculate_graham_number(eps: float, bvps: float) -> Decimal:
        """
        Graham Number (벤저민 그레이엄 공식)
        
        Formula: √(22.5 × EPS × BVPS)
        
        Args:
            eps: 주당 순이익 (TTM)
            bvps: 주당 순자산 (Book Value Per Share)
        
        Returns:
            적정가격
        """
        if eps <= 0 or bvps <= 0:
            return Decimal('0')
        
        graham_value = (22.5 * eps * bvps) ** 0.5
        return Decimal(str(round(graham_value, 2)))
    
    @staticmethod
    def calculate_category_per(net_income: float, category_avg_per: float = 15.0, 
                               shares_outstanding: int = 1000000000) -> Decimal:
        """
        동종업계 평균 PER 기반 적정가
        
        Args:
            net_income: 순이익 (TTM)
            category_avg_per: 업계 평균 PER (기본 15)
            shares_outstanding: 발행 주식 수
        
        Returns:
            적정가격
        """
        if net_income <= 0:
            return Decimal('0')
        
        eps = net_income / shares_outstanding
        fair_value = eps * category_avg_per
        
        return Decimal(str(round(fair_value, 2)))
    
    @staticmethod
    def calculate_pbr_based(total_equity: float, category_avg_pbr: float = 1.5,
                           shares_outstanding: int = 1000000000) -> Decimal:
        """
        PBR 기반 적정가
        
        Args:
            total_equity: 자본총계
            category_avg_pbr: 업계 평균 PBR (기본 1.5)
            shares_outstanding: 발행 주식 수
        
        Returns:
            적정가격
        """
        if total_equity <= 0:
            return Decimal('0')
        
        bvps = total_equity / shares_outstanding
        fair_value = bvps * category_avg_pbr
        
        return Decimal(str(round(fair_value, 2)))
    
    @classmethod
    def calculate_mate_proper_price(cls, indicators: Dict, mate_type: str, 
                                   current_price: float, shares_outstanding: int = 1000000000) -> Dict:
        """
        메이트별 적정가격 계산
        
        Args:
            indicators: 재무 지표 딕셔너리
            mate_type: 'benjamin', 'fisher', 'greenblatt', 'lynch'
            current_price: 현재 주가
            shares_outstanding: 발행 주식 수
        
        Returns:
            {
                'proper_price': Decimal,
                'gap_ratio': Decimal,
                'recommendation': str,
                'method': str
            }
        """
        ttm_fcf = indicators.get('ttm_fcf', 0)
        ttm_net_income = indicators.get('ttm_net_income', 0)
        total_equity = indicators.get('total_equity', 0)
        revenue_growth = indicators.get('revenue_growth', 0) or 0
        
        proper_price = Decimal('0')
        method = ''
        
        if mate_type == 'benjamin':
            # 벤저민: Graham Number 사용
            eps = ttm_net_income / shares_outstanding
            bvps = total_equity / shares_outstanding
            proper_price = cls.calculate_graham_number(eps, bvps)
            method = 'GRAHAM_NUMBER'
            
        elif mate_type == 'fisher':
            # 피셔: DCF (성장 중시)
            growth = min(revenue_growth / 100, 0.15)  # 최대 15%
            proper_price = cls.calculate_dcf(ttm_fcf, growth_rate=growth, shares_outstanding=shares_outstanding)
            method = 'DCF_GROWTH'
            
        elif mate_type == 'greenblatt':
            # 그린블라트: ROE 기반 PBR
            roe = indicators.get('roe', 0)
            pbr = max(roe / 10, 1.0)  # ROE 20% → PBR 2.0
            proper_price = cls.calculate_pbr_based(total_equity, category_avg_pbr=pbr, shares_outstanding=shares_outstanding)
            method = 'ROE_BASED_PBR'
            
        elif mate_type == 'lynch':
            # 린치: PEG 기반 (성장률 고려 PER)
            growth = max(revenue_growth, 5)
            peg_ratio = 1.0  # 적정 PEG = 1.0
            fair_per = growth * peg_ratio
            proper_price = cls.calculate_category_per(ttm_net_income, category_avg_per=fair_per, shares_outstanding=shares_outstanding)
            method = 'PEG_BASED'
        
        # 괴리율 계산
        if proper_price > 0 and current_price > 0:
            gap_ratio = ((current_price - float(proper_price)) / float(proper_price)) * 100
            gap_ratio = Decimal(str(round(gap_ratio, 2)))
        else:
            gap_ratio = Decimal('0')
        
        # 분석 결과 (참고용)
        if gap_ratio <= -20:
            recommendation = "🟢 20% 이상 저평가 (매우 저평가)"
        elif gap_ratio <= -10:
            recommendation = "🟢 10% 이상 저평가 (저평가)"
        elif gap_ratio <= 10:
            recommendation = "🟡 적정가 범위 (±10% 이내)"
        elif gap_ratio <= 20:
            recommendation = "🟠 10% 이상 고평가 (고평가)"
        else:
            recommendation = "🔴 20% 이상 고평가 (매우 고평가)"
        
        return {
            'proper_price': proper_price,
            'gap_ratio': gap_ratio,
            'recommendation': recommendation,
            'method': method,
        }


def calculate_all_mates_proper_price(indicators: Dict, current_price: float, 
                                     shares_outstanding: int = 1000000000) -> Dict:
    """
    4개 메이트 모두의 적정가격 계산
    
    Returns:
        {
            'benjamin': {...},
            'fisher': {...},
            'greenblatt': {...},
            'lynch': {...}
        }
    """
    results = {}
    
    for mate_type in ['benjamin', 'fisher', 'greenblatt', 'lynch']:
        results[mate_type] = ValuationEngine.calculate_mate_proper_price(
            indicators,
            mate_type,
            current_price,
            shares_outstanding
        )
    
    return results

