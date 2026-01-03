"""
GPT-4 메이트 분석 실행

DB에 저장된 재무 데이터를 기반으로 3명의 투자 대가 메이트가 분석

메이트:
1. 벤저민 그레이엄 - 안전마진, 저평가
2. 필립 피셔 - 성장성, 경영 품질
3. 조엘 그린블라트 - 마법공식 (ROIC + Earnings Yield)

사용법:
    python scripts/run_mate_analysis.py --limit 10  # 테스트용 10개
    python scripts/run_mate_analysis.py  # 전체 실행
"""

import os
import sys
import django
from datetime import datetime
import time
import csv
import json
from decimal import Decimal
import argparse

# Django 설정
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from openai import OpenAI
from apps.stocks.models import Stock, StockFinancialRaw
from apps.analysis.models import MateAnalysis


# 설정
PROGRESS_FILE = 'progress_mate_analysis.csv'
RETRY_COUNT = 2

# 통계
stats = {
    'success': 0,
    'failed': 0,
    'skipped': 0,
    'total_cost': 0.0,
}


def load_progress():
    """진행 상황 로드"""
    if not os.path.exists(PROGRESS_FILE):
        return set()
    
    processed = set()
    with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('status') == 'success':
                processed.add(row['stock_code'])
    return processed


def save_progress(stock_code, status, message='', cost=0.0):
    """진행 상황 저장"""
    file_exists = os.path.exists(PROGRESS_FILE)
    
    with open(PROGRESS_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['stock_code', 'status', 'message', 'cost', 'timestamp'])
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({
            'stock_code': stock_code,
            'status': status,
            'message': message[:100] if message else '',
            'cost': f'{cost:.4f}',
            'timestamp': datetime.now().isoformat()
        })


def calculate_indicators(stock):
    """
    재무 지표 계산
    """
    # 최근 4개 분기 데이터 (TTM)
    recent_financials = StockFinancialRaw.objects.filter(
        stock=stock,
        data_source='EDGAR'
    ).order_by('-disclosure_year', '-disclosure_quarter')[:4]
    
    if len(recent_financials) < 4:
        return None
    
    # TTM 계산
    ttm_data = {
        'ocf': sum([f.ocf or 0 for f in recent_financials]),
        'fcf': sum([f.fcf or 0 for f in recent_financials]),
        'net_income': sum([f.net_income or 0 for f in recent_financials]),
        'revenue': sum([f.revenue or 0 for f in recent_financials]),
    }
    
    # 최근 분기 재무상태
    latest = recent_financials[0]
    
    # 기본 체크
    if not latest.total_assets or not latest.total_equity:
        return None
    
    # 지표 계산
    indicators = {
        'stock_name': stock.stock_name,
        'stock_code': stock.stock_code,
        
        # 현금흐름
        'ocf': ttm_data['ocf'],
        'fcf': ttm_data['fcf'],
        'net_income': ttm_data['net_income'],
        'revenue': ttm_data['revenue'],
        
        # 재무상태
        'total_assets': latest.total_assets,
        'total_liabilities': latest.total_liabilities or 0,
        'total_equity': latest.total_equity,
        'current_assets': latest.current_assets or 0,
        'current_liabilities': latest.current_liabilities or 0,
        
        # 비율 계산
        'roe': round((ttm_data['net_income'] / latest.total_equity) * 100, 2) if latest.total_equity else 0,
        'debt_ratio': round((latest.total_liabilities / latest.total_equity) * 100, 2) if latest.total_equity else 0,
        'current_ratio': round((latest.current_assets / latest.current_liabilities) * 100, 2) if latest.current_liabilities else 0,
        'fcf_margin': round((ttm_data['fcf'] / ttm_data['revenue']) * 100, 2) if ttm_data['revenue'] else 0,
    }
    
    return indicators


def analyze_with_benjamin(indicators, client):
    """벤저민 그레이엄 메이트 분석"""
    prompt = f"""
당신은 벤저민 그레이엄의 투자 철학을 따르는 AI 분석가입니다.

투자 원칙:
• 안전마진 최우선
• 재무 안전성 중시 (부채비율, 유동비율)
• 현금흐름 품질

기업 정보:
- 기업명: {indicators['stock_name']}
- ROE: {indicators['roe']}%
- 부채비율: {indicators['debt_ratio']}%
- 유동비율: {indicators['current_ratio']}%
- FCF 마진: {indicators['fcf_margin']}%
- OCF: ${indicators['ocf']:,.0f}
- FCF: ${indicators['fcf']:,.0f}

당신의 투자 철학에 따라 이 기업을 평가하세요.

응답 형식 (JSON):
{{
  "score": 0-100 점수,
  "summary": "한 줄 요약 (30자 이내)",
  "reason": "평가 이유 (3-4줄, 쉬운 언어, 구체적 숫자 포함)",
  "caution": "주의사항 (있다면)",
  "score_detail": {{
    "safety": 0-100,
    "cashflow": 0-100,
    "stability": 0-100
  }}
}}

말투: 신중하고 정중한 톤
"""
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "벤저민 그레이엄 스타일 투자 분석가"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    tokens = response.usage.total_tokens
    cost = (tokens / 1000) * 0.01  # GPT-4 Turbo 비용
    
    return result, cost


def analyze_with_fisher(indicators, client):
    """필립 피셔 메이트 분석"""
    prompt = f"""
당신은 필립 피셔의 투자 철학을 따르는 AI 분석가입니다.

투자 원칙:
• 성장성 중시
• 현금흐름 창출 능력
• 장기 투자

기업 정보:
- 기업명: {indicators['stock_name']}
- ROE: {indicators['roe']}%
- OCF: ${indicators['ocf']:,.0f}
- FCF: ${indicators['fcf']:,.0f}
- FCF 마진: {indicators['fcf_margin']}%
- 매출: ${indicators['revenue']:,.0f}

당신의 투자 철학에 따라 이 기업의 성장성을 평가하세요.

응답 형식 (JSON):
{{
  "score": 0-100 점수,
  "summary": "한 줄 요약 (30자 이내)",
  "reason": "평가 이유 (3-4줄, 쉬운 언어, 구체적 숫자 포함)",
  "caution": "주의사항 (있다면)",
  "score_detail": {{
    "growth": 0-100,
    "quality": 0-100,
    "management": 0-100
  }}
}}

말투: 열정적이고 미래 지향적
"""
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "필립 피셔 스타일 투자 분석가"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    tokens = response.usage.total_tokens
    cost = (tokens / 1000) * 0.01
    
    return result, cost


def analyze_with_greenblatt(indicators, client):
    """조엘 그린블라트 메이트 분석"""
    
    # ROIC 계산 (간이버전: ROE 사용)
    roic = indicators['roe']
    
    # Earnings Yield 계산 (간이버전: Net Income / Total Assets)
    earnings_yield = (indicators['net_income'] / indicators['total_assets'] * 100) if indicators['total_assets'] else 0
    
    prompt = f"""
당신은 조엘 그린블라트의 마법공식을 따르는 AI 분석가입니다.

투자 원칙:
• 좋은 회사 (높은 ROIC)
• 싼 가격 (높은 Earnings Yield)
• 계량적 분석

기업 정보:
- 기업명: {indicators['stock_name']}
- ROIC (ROE): {roic:.2f}%
- Earnings Yield: {earnings_yield:.2f}%
- FCF: ${indicators['fcf']:,.0f}
- 총자산: ${indicators['total_assets']:,.0f}

당신의 마법공식에 따라 이 기업을 평가하세요.

응답 형식 (JSON):
{{
  "score": 0-100 점수,
  "summary": "한 줄 요약 (30자 이내)",
  "reason": "평가 이유 (3-4줄, 쉬운 언어, 구체적 숫자 포함)",
  "caution": "주의사항 (있다면)",
  "score_detail": {{
    "roic": 0-100,
    "earnings_yield": 0-100,
    "value": 0-100
  }}
}}

말투: 명확하고 논리적
"""
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "조엘 그린블라트 스타일 투자 분석가"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    tokens = response.usage.total_tokens
    cost = (tokens / 1000) * 0.01
    
    return result, cost


def analyze_stock(stock, client):
    """
    단일 종목 분석 (3명 메이트)
    """
    # 1. 재무 지표 계산
    indicators = calculate_indicators(stock)
    if not indicators:
        return None, "재무 데이터 부족"
    
    total_cost = 0.0
    
    try:
        # 2. 벤저민 분석
        benjamin_result, cost1 = analyze_with_benjamin(indicators, client)
        time.sleep(0.5)  # Rate limit
        
        # 3. 피셔 분석
        fisher_result, cost2 = analyze_with_fisher(indicators, client)
        time.sleep(0.5)
        
        # 4. 그린블라트 분석
        greenblatt_result, cost3 = analyze_with_greenblatt(indicators, client)
        time.sleep(0.5)
        
        total_cost = cost1 + cost2 + cost3
        
        # 5. DB 저장
        for mate_type, result in [
            ('benjamin', benjamin_result),
            ('fisher', fisher_result),
            ('greenblatt', greenblatt_result)
        ]:
            MateAnalysis.objects.update_or_create(
                stock=stock,
                mate_type=mate_type,
                defaults={
                    'score': result['score'],
                    'summary': result['summary'],
                    'reason': result['reason'],
                    'caution': result.get('caution', ''),
                    'score_detail': result['score_detail'],
                }
            )
        
        return total_cost, None
        
    except Exception as e:
        return None, str(e)[:100]


def run_mate_analysis(api_key, limit=None):
    """
    메이트 분석 실행
    """
    print("=" * 60)
    print("🤖 GPT-4 메이트 분석")
    print("=" * 60)
    print()
    
    # OpenAI 클라이언트
    client = OpenAI(api_key=api_key)
    
    # 1. 진행 상황 로드
    print("📂 진행 상황 확인 중...")
    processed_codes = load_progress()
    if processed_codes:
        print(f"✅ 이미 처리된 종목: {len(processed_codes)}개 (건너뛰기)")
    print()
    
    # 2. 분석할 종목 조회 (재무 데이터가 있는 종목만)
    print("🔍 분석 대상 종목 조회 중...")
    
    stocks_with_data = StockFinancialRaw.objects.filter(
        data_source='EDGAR'
    ).values_list('stock_id', flat=True).distinct()
    
    stocks = Stock.objects.filter(
        id__in=stocks_with_data,
        country='us'
    ).exclude(
        stock_code__in=processed_codes
    ).order_by('stock_code')
    
    if limit:
        stocks = stocks[:limit]
        print(f"⚠️  테스트 모드: {limit}개만 처리")
    
    total = stocks.count()
    print(f"✅ 분석 대상: {total}개")
    print()
    
    if total == 0:
        print("✅ 모든 종목이 이미 분석되었습니다!")
        return
    
    # 3. 분석 시작
    print("=" * 60)
    print("🚀 메이트 분석 시작!")
    print("=" * 60)
    print()
    
    start_time = time.time()
    
    for idx, stock in enumerate(stocks, 1):
        try:
            print(f"[{idx}/{total}] 🔍 {stock.stock_code}: {stock.stock_name[:30]}")
            
            cost, error = analyze_stock(stock, client)
            
            if cost is not None:
                stats['success'] += 1
                stats['total_cost'] += cost
                save_progress(stock.stock_code, 'success', '3명 분석 완료', cost)
                
                print(f"        ✅ 완료 (${cost:.4f})")
                print(f"        💰 누적: ${stats['total_cost']:.2f}")
            else:
                stats['failed'] += 1
                save_progress(stock.stock_code, 'failed', error)
                print(f"        ❌ 실패: {error}")
            
            print()
            
        except Exception as e:
            stats['failed'] += 1
            save_progress(stock.stock_code, 'error', str(e)[:100])
            print(f"        ❌ 에러: {str(e)[:50]}\n")
    
    elapsed_time = time.time() - start_time
    
    # 4. 최종 통계
    print()
    print("=" * 60)
    print("📊 분석 완료!")
    print("=" * 60)
    print(f"✅ 성공: {stats['success']}개")
    print(f"❌ 실패: {stats['failed']}개")
    print(f"💰 총 비용: ${stats['total_cost']:.2f}")
    print(f"⏱️  소요 시간: {elapsed_time/60:.1f}분")
    print()
    
    # DB 통계
    total_analyses = MateAnalysis.objects.count()
    total_stocks_analyzed = MateAnalysis.objects.values('stock').distinct().count()
    
    print(f"💾 DB 통계:")
    print(f"  - 메이트 분석: {total_analyses}개")
    print(f"  - 분석된 종목: {total_stocks_analyzed}개")
    print()
    
    if limit:
        remaining = Stock.objects.filter(
            id__in=stocks_with_data,
            country='us'
        ).exclude(
            stock_code__in=load_progress()
        ).count()
        
        estimated_cost = (stats['total_cost'] / stats['success']) * remaining if stats['success'] > 0 else 0
        
        print(f"📊 전체 실행 예상:")
        print(f"  - 남은 종목: {remaining}개")
        print(f"  - 예상 비용: ${estimated_cost:.2f}")
        print(f"  - 예상 시간: {(elapsed_time / stats['success'] * remaining / 60):.0f}분")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='GPT-4 메이트 분석')
    parser.add_argument('--limit', type=int, help='처리할 종목 수 제한 (테스트용)')
    parser.add_argument('--api-key', type=str, help='OpenAI API Key')
    args = parser.parse_args()
    
    # API 키 입력
    api_key = args.api_key
    if not api_key:
        api_key = input("🔑 OpenAI API Key 입력: ").strip()
    
    if not api_key:
        print("❌ API 키가 필요합니다!")
        sys.exit(1)
    
    run_mate_analysis(api_key, limit=args.limit)

