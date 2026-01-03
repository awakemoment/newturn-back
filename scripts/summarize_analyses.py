"""
15개 종목 분석 결과 요약
"""
import json
import glob


def load_all_analyses():
    """모든 분석 파일 로드"""
    files = glob.glob('data/qual_*.json')
    analyses = {}
    
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            analyses[data['ticker']] = data
    
    return analyses


def print_summary(analyses):
    """요약 출력"""
    
    print("="*80)
    print("📊 Top 15 종목 정성적 분석 결과")
    print("="*80)
    print()
    
    # 메이트별 평균 점수
    mate_scores = {'benjamin': [], 'fisher': [], 'greenblatt': [], 'daily': []}
    
    for ticker in sorted(analyses.keys()):
        data = analyses[ticker]
        print(f"\n{'='*80}")
        print(f"🏢 {ticker} - {data.get('company_name', 'N/A')}")
        print('='*80)
        
        # 비즈니스 모델
        bm = data.get('business_model', {})
        print(f"💼 비즈니스: {bm.get('model_type', 'N/A')}")
        print(f"   이해도: {bm.get('understandability_score', 0)}/10")
        
        # 경쟁우위
        moat = data.get('competitive_advantages', {})
        print(f"🏰 Moat: {moat.get('moat_strength', 'N/A')}")
        
        # 리스크
        risks = data.get('risks', {})
        print(f"⚠️  리스크: {risks.get('overall_risk_level', 'N/A')} ({risks.get('risk_score', 0)}/100)")
        
        # 투자 매력도
        appeal = data.get('investment_appeal', {})
        print(f"⭐ 종합: {appeal.get('overall_score', 0)}/100 ({appeal.get('grade', 'N/A')})")
        
        # 메이트 평가
        print(f"\n🤖 메이트 평가:")
        mates = data.get('mate_assessments', {})
        for mate_id, mate_name in [('benjamin', '베니'), ('fisher', '그로우'), ('greenblatt', '매직'), ('daily', '데일리')]:
            mate_data = mates.get(mate_id, {})
            score = mate_data.get('score', 0)
            assessment = mate_data.get('assessment', 'N/A')
            
            mate_scores[mate_id].append(score)
            
            print(f"  {mate_name:8s}: {score:3d}점 - {assessment}")
    
    # 메이트별 통계
    print(f"\n\n{'='*80}")
    print("📊 메이트별 평균 점수")
    print('='*80)
    
    for mate_id, mate_name in [('benjamin', '베니 (안전마진)'), ('fisher', '그로우 (성장)'), ('greenblatt', '매직 (마법공식)'), ('daily', '데일리 (일상)')]:
        scores = mate_scores[mate_id]
        avg = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0
        
        print(f"\n{mate_name}")
        print(f"  평균: {avg:.1f}점")
        print(f"  최고: {max_score}점")
        print(f"  최저: {min_score}점")
    
    # Top 5 종목 (메이트별)
    print(f"\n\n{'='*80}")
    print("🏆 메이트별 Top 5 종목")
    print('='*80)
    
    for mate_id, mate_name in [('benjamin', '베니'), ('fisher', '그로우'), ('greenblatt', '매직'), ('daily', '데일리')]:
        print(f"\n{mate_name}의 Top 5:")
        
        # 정렬
        sorted_stocks = sorted(
            analyses.items(),
            key=lambda x: x[1].get('mate_assessments', {}).get(mate_id, {}).get('score', 0),
            reverse=True
        )[:5]
        
        for i, (ticker, data) in enumerate(sorted_stocks, 1):
            score = data.get('mate_assessments', {}).get(mate_id, {}).get('score', 0)
            print(f"  {i}. {ticker:6s} - {score}점")


if __name__ == "__main__":
    analyses = load_all_analyses()
    print(f"\n총 {len(analyses)}개 종목 분석 로드됨\n")
    print_summary(analyses)


