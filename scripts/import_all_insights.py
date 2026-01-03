"""
전체 15개 종목 인사이트 DB 임포트

1. 정성적 분석 (QualitativeAnalysis)
2. 메이트 점수 (MateAnalysis)
3. 10-K 인사이트 (TenKInsight)
"""
import os
import sys
import django
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock
from apps.analysis.models import QualitativeAnalysis, MateAnalysis, TenKInsight
from datetime import datetime


def import_aapl_structured_data():
    """AAPL 구조화 데이터 임포트"""
    
    with open('data/aapl_structured_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stock = Stock.objects.get(stock_code='AAPL')
    
    # TenKInsight 생성
    insight, created = TenKInsight.objects.update_or_create(
        stock=stock,
        fiscal_year=2024,
        defaults={
            'filing_date': '2025-10-31',
            'product_revenue': data['product_revenue'],
            'geographic_revenue': data['geographic_revenue'],
            'gross_margin': 45.5,
            'operating_margin': 30.7,
            'net_margin': 25.3,
            'rd_investment': 29900,
            'rd_as_pct_revenue': 7.7,
            'new_risks': [
                'U.S. Tariffs (2025 Q2)',
                'China market share decline',
                'AI content liability',
            ],
            'key_changes': [
                {'type': 'revenue_decline', 'item': 'Greater China', 'value': -8.0},
                {'type': 'revenue_growth', 'item': 'Services', 'value': 13.0},
                {'type': 'product_launch', 'item': 'Vision Pro', 'impact': 'new_category'},
            ],
        }
    )
    
    action = "생성" if created else "업데이트"
    print(f"✅ AAPL TenKInsight {action}")
    
    return insight


def import_all_qualitative():
    """전체 정성적 분석 재확인"""
    
    stocks_with_qual = QualitativeAnalysis.objects.count()
    stocks_with_mate = Stock.objects.filter(mate_analyses__isnull=False).distinct().count()
    
    print(f"\n📊 현재 DB 상태:")
    print(f"  정성적 분석: {stocks_with_qual}개 종목")
    print(f"  메이트 분석: {stocks_with_mate}개 종목")
    
    return {
        'qualitative_count': stocks_with_qual,
        'mate_count': stocks_with_mate,
    }


if __name__ == "__main__":
    print("="*80)
    print("📥 전체 인사이트 DB 임포트")
    print("="*80)
    
    # 1. AAPL 구조화 데이터
    print("\n1️⃣ AAPL 구조화 데이터...")
    import_aapl_structured_data()
    
    # 2. 현재 상태 확인
    print("\n2️⃣ 현재 DB 상태 확인...")
    stats = import_all_qualitative()
    
    print(f"\n{'='*80}")
    print("🎉 임포트 완료!")
    print("="*80)
    
    print("\n💡 다음 단계:")
    print("  1. 나머지 14개 종목 구조화 데이터 추출")
    print("  2. TenKInsight 대량 임포트")
    print("  3. API 노출")
    print("  4. 프론트엔드 UI")
    print()
    print("="*80)

