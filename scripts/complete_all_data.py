"""
전체 데이터 완성 자동화 스크립트

실행 순서:
1. EDGAR 수집 상태 확인
2. 메이트 점수 계산 (신규 종목)
3. 최종 현황 출력
"""
import os
import sys
import django
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock, StockFinancialRaw
from apps.analysis.models import MateAnalysis


def check_status():
    """현재 데이터 상태 확인"""
    print("\n" + "="*70)
    print("📊 데이터 현황 확인")
    print("="*70)
    
    total_stocks = Stock.objects.filter(country='us').count()
    edgar_stocks = Stock.objects.filter(financials_raw__data_source='EDGAR').distinct().count()
    mate_stocks = MateAnalysis.objects.values('stock').distinct().count()
    
    print(f"\n✅ 총 종목: {total_stocks:,}개")
    print(f"✅ EDGAR 데이터: {edgar_stocks:,}개 ({edgar_stocks/total_stocks*100:.1f}%)")
    print(f"✅ 메이트 분석: {mate_stocks:,}개 ({mate_stocks/total_stocks*100:.1f}%)")
    
    # 메이트 점수 없는 EDGAR 종목
    edgar_stock_ids = Stock.objects.filter(
        financials_raw__data_source='EDGAR'
    ).distinct().values_list('id', flat=True)
    
    mate_stock_ids = MateAnalysis.objects.values_list('stock_id', flat=True).distinct()
    
    need_mate_calc = set(edgar_stock_ids) - set(mate_stock_ids)
    
    print(f"\n🎯 메이트 점수 계산 필요: {len(need_mate_calc):,}개")
    
    return {
        'total': total_stocks,
        'edgar': edgar_stocks,
        'mate': mate_stocks,
        'need_mate': len(need_mate_calc),
    }


def calculate_missing_mates():
    """메이트 점수가 없는 종목 계산"""
    print("\n" + "="*70)
    print("🤖 메이트 점수 계산")
    print("="*70)
    
    result = subprocess.run(
        [sys.executable, 'scripts/calculate_mate_scores.py'],
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    if result.returncode != 0:
        print(f"\n❌ 에러:\n{result.stderr}")
        return False
    
    return True


def main():
    print("\n" + "="*70)
    print("🚀 전체 데이터 완성 자동화")
    print("="*70)
    
    # Step 1: 현황 확인
    status = check_status()
    
    # Step 2: 메이트 점수 계산 필요 여부
    if status['need_mate'] > 0:
        print(f"\n📌 {status['need_mate']:,}개 종목에 대해 메이트 점수 계산 시작...")
        
        success = calculate_missing_mates()
        
        if success:
            print("\n✅ 메이트 점수 계산 완료!")
        else:
            print("\n❌ 메이트 점수 계산 실패!")
            return
    else:
        print("\n✅ 모든 종목의 메이트 점수가 이미 계산되어 있습니다!")
    
    # Step 3: 최종 확인
    print("\n" + "="*70)
    print("📊 최종 데이터 현황")
    print("="*70)
    
    final_status = check_status()
    
    print("\n" + "="*70)
    print("🎉 데이터 완성!")
    print("="*70)
    print(f"\n✅ EDGAR: {final_status['edgar']:,}개")
    print(f"✅ 메이트: {final_status['mate']:,}개")
    print(f"✅ 커버리지: {final_status['mate']/final_status['total']*100:.1f}%")
    print("\n무료 베타 출시 준비 완료! 🚀\n")


if __name__ == '__main__':
    main()

