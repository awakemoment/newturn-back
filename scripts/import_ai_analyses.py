"""
AI 분석 결과를 Django DB에 저장

모든 JSON 파일을 읽어서:
1. TenKInsight 모델에 저장
2. QualitativeAnalysis 업데이트 (필요 시)
3. MateAnalysis 점수 조정
"""
import os
import sys
import json
import django

# Django 설정
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock
from apps.analysis.models import TenKInsight, MateAnalysis
from datetime import date


def import_all_analyses():
    """모든 AI 분석 결과 임포트"""
    
    print("="*80)
    print("📥 AI 분석 결과 DB 저장")
    print("="*80)
    
    STOCKS = ['AAPL', 'META', 'NVDA', 'AMZN', 'TSLA', 'MSFT', 'GOOGL', 'V']
    
    imported_count = 0
    
    for ticker in STOCKS:
        print(f"\n{'='*80}")
        print(f"📊 {ticker} 임포트")
        print('-'*80)
        
        # Stock 객체 가져오기
        try:
            stock = Stock.objects.get(stock_code=ticker)
        except Stock.DoesNotExist:
            print(f"   ❌ Stock not found: {ticker}")
            continue
        
        # Item 7 (MD&A) 데이터 읽기
        item7_file = f'data/ai_analysis_{ticker}_item_7_mda.json'
        
        if not os.path.exists(item7_file):
            print(f"   ⚠️ Item 7 파일 없음")
            continue
        
        with open(item7_file, 'r', encoding='utf-8') as f:
            item7_data = json.load(f)
        
        # 회계연도 추출
        fiscal_year = item7_data.get('fiscal_year', 2024)
        
        # 제품별/세그먼트별 매출 추출
        product_revenue = {}
        if 'financial_performance' in item7_data:
            perf = item7_data['financial_performance']
            
            # 제품별 (AAPL)
            if 'product_performance' in perf:
                for product, data in perf['product_performance'].items():
                    product_revenue[product] = {
                        'fy2025': data.get('fy2025'),
                        'growth': data.get('growth'),
                        'share': data.get('share'),
                        'insight': data.get('insight', '')
                    }
            
            # 세그먼트별 (META, NVDA, AMZN)
            if 'segment_performance' in perf:
                for segment, data in perf['segment_performance'].items():
                    if isinstance(data, dict):
                        product_revenue[segment] = {
                            'revenue': data.get('revenue_fy2024') or data.get('fy2025'),
                            'growth': data.get('growth'),
                            'share': data.get('share')
                        }
            
            # AMZN segments
            if 'segments' in perf:
                for segment, data in perf['segments'].items():
                    product_revenue[segment] = {
                        'revenue': data.get('revenue'),
                        'growth': data.get('growth')
                    }
        
        # 신규 리스크 추출
        new_risks = []
        
        # Item 1A (Risk) 데이터 읽기
        item1a_file = f'data/ai_analysis_{ticker}_item_1a_risk_factors.json'
        
        if os.path.exists(item1a_file):
            with open(item1a_file, 'r', encoding='utf-8') as f:
                item1a_data = json.load(f)
            
            # 신규 리스크 추출
            if 'new_risks_2025' in item1a_data:
                for risk_data in item1a_data['new_risks_2025']:
                    new_risks.append(risk_data.get('risk', str(risk_data)))
            elif 'new_risks_2024_2025' in item1a_data:
                for risk_data in item1a_data['new_risks_2024_2025']:
                    new_risks.append(risk_data.get('risk', str(risk_data)))
        
        # TenKInsight 생성 또는 업데이트
        insight, created = TenKInsight.objects.update_or_create(
            stock=stock,
            fiscal_year=fiscal_year,
            defaults={
                'filing_date': date(fiscal_year, 10, 31) if ticker == 'AAPL' else date(fiscal_year, 12, 31),
                'product_revenue': product_revenue,
                'geographic_revenue': {},  # Item 7에서 추출 가능
                'new_risks': new_risks[:5],  # Top 5만
                'key_changes': [],  # 나중에 추가
            }
        )
        
        action = '생성' if created else '업데이트'
        print(f"   ✅ TenKInsight {action}: FY{fiscal_year}")
        print(f"      제품/세그먼트: {len(product_revenue)}개")
        print(f"      신규 리스크: {len(new_risks)}개")
        
        imported_count += 1
    
    print(f"\n{'='*80}")
    print(f"✅ 총 {imported_count}개 종목 임포트 완료!")
    print("="*80)


if __name__ == "__main__":
    import_all_analyses()

