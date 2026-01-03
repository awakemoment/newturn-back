"""
메이트 분석 엔진
GPT-4 기반 투자 분석
"""

import openai
import json
from django.conf import settings


class MateEngine:
    """
    AI 메이트 분석 엔진
    """
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
    
    def analyze(self, stock_data, mate_type='benjamin'):
        """
        종목 분석
        
        Args:
            stock_data (dict): 재무 데이터
            mate_type (str): 'benjamin', 'fisher', 'greenblatt', 'lynch'
        
        Returns:
            dict: {
                'score': int,
                'summary': str,
                'reason': str,
                'caution': str,
                'score_detail': dict
            }
        """
        mate_prompts = {
            'benjamin': self._get_benjamin_prompt,
            'fisher': self._get_fisher_prompt,
            'greenblatt': self._get_greenblatt_prompt,
            'lynch': self._get_lynch_prompt,
        }
        
        if mate_type not in mate_prompts:
            raise ValueError(f"Unknown mate_type: {mate_type}")
        
        prompt = mate_prompts[mate_type](stock_data)
        
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"{mate_type} 스타일 투자 분석가"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    
    def _get_benjamin_prompt(self, stock_data):
        """벤저민 그레이엄 프롬프트"""
        return f"""
당신은 벤저민 그레이엄의 투자 철학을 따릅니다.

기업: {stock_data.get('stock_name')}
PBR: {stock_data.get('pbr')}
부채비율: {stock_data.get('debt_ratio')}%
배당: {stock_data.get('dividend_yield')}%

안전마진 관점으로 평가하고 JSON으로 답변:
{{
  "score": 0-100,
  "summary": "한 줄",
  "reason": "3-4줄",
  "caution": "주의사항",
  "score_detail": {{"undervalued": 0-100, "safety": 0-100, "dividend": 0-100}}
}}
"""
    
    def _get_fisher_prompt(self, stock_data):
        """필립 피셔 프롬프트"""
        return f"""
당신은 필립 피셔의 투자 철학을 따릅니다.

기업: {stock_data.get('stock_name')}
매출 성장: {stock_data.get('revenue_growth_3y')}%
R&D 비중: {stock_data.get('rd_ratio')}%

성장과 경영진 관점으로 평가하고 JSON으로 답변.
"""
    
    def _get_greenblatt_prompt(self, stock_data):
        """조엘 그린블라트 프롬프트"""
        return f"""
당신은 조엘 그린블라트의 마법공식을 따릅니다.

기업: {stock_data.get('stock_name')}
ROE: {stock_data.get('roe')}%
PER: {stock_data.get('per')}

우량도와 염가도로 평가하고 JSON으로 답변.
"""
    
    def _get_lynch_prompt(self, stock_data):
        """피터 린치 프롬프트"""
        return f"""
당신은 피터 린치의 투자 철학을 따릅니다.

기업: {stock_data.get('stock_name')}
성장률: {stock_data.get('eps_growth_3y')}%
PER: {stock_data.get('per')}

이해하기 쉬운 기업인지 평가하고 JSON으로 답변.
"""

