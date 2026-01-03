"""
현재 DB 데이터 현황 확인 스크립트
"""
import os
import sys
import django

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock, StockFinancialRaw
from apps.analysis.models import MateAnalysis, QualitativeAnalysis

def main():
    print("\n" + "="*70)
    print("📊 NEWTURN 데이터 현황")
    print("="*70)
    
    # 1. 종목 현황
    print("\n🏢 종목 현황:")
    print("-" * 70)
    total_stocks = Stock.objects.count()
    us_stocks = Stock.objects.filter(country='us').count()
    kr_stocks = Stock.objects.filter(country='kr').count()
    
    print(f"  전체 종목: {total_stocks:,}개")
    print(f"  └─ 미국(US): {us_stocks:,}개")
    print(f"  └─ 한국(KR): {kr_stocks:,}개")
    
    # 2. 재무 데이터 현황
    print("\n💰 재무 데이터 현황:")
    print("-" * 70)
    
    edgar_stocks = Stock.objects.filter(
        financials_raw__data_source='EDGAR'
    ).distinct().count()
    
    dart_stocks = Stock.objects.filter(
        financials_raw__data_source='DART'
    ).distinct().count()
    
    total_financials = StockFinancialRaw.objects.count()
    edgar_financials = StockFinancialRaw.objects.filter(data_source='EDGAR').count()
    
    print(f"  EDGAR 데이터 보유 종목: {edgar_stocks:,}개")
    print(f"  DART 데이터 보유 종목: {dart_stocks:,}개")
    print(f"  총 재무 데이터 레코드: {total_financials:,}개")
    print(f"    └─ EDGAR: {edgar_financials:,}개")
    
    # 3. 메이트 분석 현황
    print("\n🤖 메이트 분석 현황:")
    print("-" * 70)
    
    mate_stocks = MateAnalysis.objects.values('stock').distinct().count()
    total_analyses = MateAnalysis.objects.count()
    
    benjamin_count = MateAnalysis.objects.filter(mate_type='benjamin').count()
    fisher_count = MateAnalysis.objects.filter(mate_type='fisher').count()
    greenblatt_count = MateAnalysis.objects.filter(mate_type='greenblatt').count()
    lynch_count = MateAnalysis.objects.filter(mate_type='lynch').count()
    
    print(f"  메이트 분석 완료 종목: {mate_stocks:,}개")
    print(f"  총 분석 레코드: {total_analyses:,}개")
    print(f"    🎩 베니 (Benjamin): {benjamin_count:,}개")
    print(f"    🌱 그로우 (Fisher): {fisher_count:,}개")
    print(f"    🔮 매직 (Greenblatt): {greenblatt_count:,}개")
    print(f"    🎯 데일리 (Lynch): {lynch_count:,}개")
    
    # 4. 정성 분석 현황
    print("\n📄 정성 분석 (10-K) 현황:")
    print("-" * 70)
    
    qualitative_count = QualitativeAnalysis.objects.count()
    print(f"  정성 분석 완료 종목: {qualitative_count:,}개")
    
    if qualitative_count > 0:
        qual_stocks = QualitativeAnalysis.objects.values_list('stock__stock_code', flat=True)[:10]
        print(f"  샘플: {', '.join(qual_stocks)}")
    
    # 5. 데이터 완성도
    print("\n✅ 데이터 완성도:")
    print("-" * 70)
    
    if us_stocks > 0:
        edgar_coverage = (edgar_stocks / us_stocks) * 100
        mate_coverage = (mate_stocks / us_stocks) * 100
        
        print(f"  EDGAR 커버리지: {edgar_coverage:.1f}% ({edgar_stocks}/{us_stocks})")
        print(f"  메이트 분석 커버리지: {mate_coverage:.1f}% ({mate_stocks}/{us_stocks})")
    
    # 6. Top 10 종목 (메이트 점수 기준)
    print("\n🏆 메이트 점수 Top 10 종목:")
    print("-" * 70)
    
    from django.db.models import Avg
    
    top_stocks = MateAnalysis.objects.values(
        'stock__stock_code', 
        'stock__stock_name'
    ).annotate(
        avg_score=Avg('score')
    ).order_by('-avg_score')[:10]
    
    for i, stock in enumerate(top_stocks, 1):
        code = stock['stock__stock_code']
        name = stock['stock__stock_name'][:20]  # 이름 길이 제한
        score = stock['avg_score']
        print(f"  {i:2d}. {code:6s} - {name:20s} (평균: {score:.1f}점)")
    
    print("\n" + "="*70)
    print("✅ 확인 완료!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()

