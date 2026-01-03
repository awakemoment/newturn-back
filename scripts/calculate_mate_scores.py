"""
모든 종목의 메이트 점수 계산 및 저장

사용법:
    python scripts/calculate_mate_scores.py
    python scripts/calculate_mate_scores.py --limit 10  # 테스트용
"""
import os
import sys
import django
import argparse

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock, StockFinancialRaw
from apps.analysis.models import MateAnalysis
from core.utils.mate_engines import analyze_with_all_mates


def calculate_indicators(stock):
    """종목의 지표 계산"""
    try:
        # 최근 4분기
        recent_4q = list(StockFinancialRaw.objects.filter(
            stock=stock,
            data_source='EDGAR'
        ).order_by('-disclosure_year', '-disclosure_quarter')[:4])
        
        if len(recent_4q) < 4:
            return None
        
        # TTM 계산
        ttm_ocf = sum([q.ocf or 0 for q in recent_4q])
        ttm_fcf = sum([q.fcf or 0 for q in recent_4q])
        ttm_revenue = sum([q.revenue or 0 for q in recent_4q])
        ttm_net_income = sum([q.net_income or 0 for q in recent_4q])
        
        latest = recent_4q[0]
        
        if not latest.total_equity:
            return None
        
        # 지표 계산
        fcf_margin = round((ttm_fcf / ttm_revenue) * 100, 2) if ttm_revenue else 0
        roe = round((ttm_net_income / latest.total_equity) * 100, 2)
        debt_ratio = round((latest.total_liabilities / latest.total_equity) * 100, 2) if latest.total_equity else 0
        current_ratio = round((latest.current_assets / latest.current_liabilities) * 100, 2) if latest.current_liabilities else 0
        
        # 성장률
        previous_4q = list(StockFinancialRaw.objects.filter(
            stock=stock,
            data_source='EDGAR'
        ).order_by('-disclosure_year', '-disclosure_quarter')[4:8])
        
        revenue_growth = None
        fcf_growth = None
        
        if len(previous_4q) == 4:
            prev_revenue = sum([q.revenue or 0 for q in previous_4q])
            prev_fcf = sum([q.fcf or 0 for q in previous_4q])
            
            if prev_revenue:
                revenue_growth = round(((ttm_revenue - prev_revenue) / prev_revenue) * 100, 2)
            if prev_fcf and prev_fcf != 0:
                fcf_growth = round(((ttm_fcf - prev_fcf) / abs(prev_fcf)) * 100, 2)
        
        # FCF 양수 분기
        all_financials = list(StockFinancialRaw.objects.filter(
            stock=stock,
            data_source='EDGAR'
        ).order_by('-disclosure_year', '-disclosure_quarter')[:20])
        
        fcf_positive_quarters = len([q for q in all_financials if q.fcf and q.fcf > 0])
        
        return {
            'ttm_fcf': ttm_fcf,
            'ttm_revenue': ttm_revenue,
            'ttm_net_income': ttm_net_income,
            'fcf_margin': fcf_margin,
            'roe': roe,
            'debt_ratio': debt_ratio,
            'current_ratio': current_ratio,
            'revenue_growth': revenue_growth,
            'fcf_growth': fcf_growth,
            'fcf_positive_quarters': fcf_positive_quarters,
        }
        
    except Exception as e:
        print(f"   ⚠️ 지표 계산 실패: {e}")
        return None


def save_mate_analyses(stock, mate_results):
    """메이트 분석 결과 저장"""
    saved_count = 0
    
    for mate_id, analysis in mate_results.items():
        try:
            # 기존 분석 업데이트 또는 생성
            MateAnalysis.objects.update_or_create(
                stock=stock,
                mate_type=mate_id,
                defaults={
                    'score': analysis['score'],
                    'summary': analysis['summary'],
                    'reason': '\n'.join(analysis.get('reasons', [])),
                    'caution': '\n'.join(analysis.get('cautions', [])),
                    'score_detail': analysis.get('details', {}),
                }
            )
            saved_count += 1
        except Exception as e:
            print(f"   ⚠️ {mate_id} 저장 실패: {e}")
    
    return saved_count


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='메이트 점수 계산')
    parser.add_argument('--limit', type=int, help='계산할 종목 수 제한')
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🤖 메이트 점수 계산 시작")
    print("="*60)
    
    # 재무 데이터가 있는 종목만
    stocks_with_data = StockFinancialRaw.objects.filter(
        data_source='EDGAR'
    ).values_list('stock_id', flat=True).distinct()
    
    stocks = Stock.objects.filter(
        id__in=stocks_with_data,
        country='us',
        is_active=True
    )
    
    if args.limit:
        stocks = stocks[:args.limit]
        print(f"📊 테스트 모드: {args.limit}개 종목만 계산")
    
    total = stocks.count()
    print(f"📊 총 {total}개 종목")
    print()
    
    success_count = 0
    fail_count = 0
    
    for i, stock in enumerate(stocks, 1):
        print(f"[{i}/{total}] {stock.stock_code} - {stock.stock_name}")
        
        # 지표 계산
        indicators = calculate_indicators(stock)
        
        if not indicators:
            print(f"   ❌ 데이터 부족")
            fail_count += 1
            continue
        
        # 모든 메이트로 분석
        mate_results = analyze_with_all_mates(indicators)
        
        # 저장
        saved = save_mate_analyses(stock, mate_results)
        
        if saved == 4:
            print(f"   ✅ 메이트 {saved}개 분석 완료")
            print(f"      🎩 베니: {mate_results['benjamin']['score']}점")
            print(f"      🌱 그로우: {mate_results['fisher']['score']}점")
            print(f"      🔮 매직: {mate_results['greenblatt']['score']}점")
            print(f"      🎯 데일리: {mate_results['lynch']['score']}점")
            success_count += 1
        else:
            print(f"   ⚠️ 일부 메이트만 저장됨 ({saved}/4)")
            fail_count += 1
        
        # 진행 상황
        if i % 10 == 0:
            print(f"\n📊 진행률: {i}/{total} ({(i/total*100):.1f}%)")
            print(f"   성공: {success_count}개 | 실패: {fail_count}개\n")
    
    # 최종 결과
    print("\n" + "="*60)
    print("🎉 메이트 점수 계산 완료!")
    print("="*60)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print(f"📊 성공률: {(success_count/(success_count+fail_count)*100):.1f}%")
    print("="*60)


if __name__ == '__main__':
    main()



