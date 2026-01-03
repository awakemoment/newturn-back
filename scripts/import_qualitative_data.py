"""
정성적 분석 데이터 DB에 임포트

Usage: python scripts/import_qualitative_data.py
"""
import os
import sys
import django
import json
import glob

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock
from apps.analysis.models import MateAnalysis, QualitativeAnalysis


def import_qualitative_analyses():
    """정성적 분석 데이터 임포트"""
    
    print("="*70)
    print("📥 정성적 분석 데이터 임포트")
    print("="*70)
    
    # JSON 파일 찾기
    json_files = glob.glob('data/qual_*.json')
    
    print(f"\n발견된 파일: {len(json_files)}개")
    
    success_count = 0
    fail_count = 0
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            ticker = data['ticker']
            print(f"\n{'='*70}")
            print(f"📊 {ticker} 임포트 중...")
            
            # Stock 찾기
            try:
                stock = Stock.objects.get(stock_code=ticker)
            except Stock.DoesNotExist:
                print(f"   ⚠️ Stock {ticker} not found. Skipping...")
                fail_count += 1
                continue
            
            # 1. QualitativeAnalysis 저장
            bm = data.get('business_model', {})
            moat = data.get('competitive_advantages', {})
            risks = data.get('risks', {})
            appeal = data.get('investment_appeal', {})
            
            qual, created = QualitativeAnalysis.objects.update_or_create(
                stock=stock,
                defaults={
                    'business_model_type': bm.get('model_type', ''),
                    'business_description': bm.get('description', ''),
                    'understandability_score': bm.get('understandability_score', 5),
                    'understandability_reason': bm.get('reason', ''),
                    
                    'moat_strength': moat.get('moat_strength', ''),
                    'moat_sustainability': moat.get('moat_sustainability', 5),
                    'moat_factors': moat.get('moat_factors', []),
                    
                    'overall_risk_level': risks.get('overall_risk_level', ''),
                    'risk_score': risks.get('risk_score', 50),
                    'top_risks': risks.get('top_3_risks', []),
                    
                    'investment_score': appeal.get('overall_score', 50),
                    'investment_grade': appeal.get('grade', 'C'),
                    'strengths': appeal.get('strengths', [])[:5],
                    'weaknesses': appeal.get('weaknesses', [])[:5],
                    'sustainability_score': appeal.get('sustainability_score', 5),
                }
            )
            
            action = "생성" if created else "업데이트"
            print(f"   ✅ QualitativeAnalysis {action}")
            
            # 2. MateAnalysis 저장 (4개 메이트)
            mates_data = data.get('mate_assessments', {})
            
            mate_mapping = {
                'benjamin': 'benjamin',
                'fisher': 'fisher',
                'greenblatt': 'greenblatt',
                'daily': 'lynch',  # daily → lynch (모델 choices와 맞춤)
            }
            
            for mate_key, mate_type in mate_mapping.items():
                mate_info = mates_data.get(mate_key, {})
                
                if not mate_info:
                    continue
                
                MateAnalysis.objects.update_or_create(
                    stock=stock,
                    mate_type=mate_type,
                    defaults={
                        'score': mate_info.get('score', 50),
                        'summary': mate_info.get('assessment', ''),
                        'reason': mate_info.get('verdict', ''),
                        'caution': mate_info.get('recommendation', ''),
                    }
                )
            
            print(f"   ✅ MateAnalysis 4개 저장 완료")
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ 오류: {e}")
            fail_count += 1
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*70}")
    print(f"🎉 임포트 완료!")
    print(f"{'='*70}")
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print(f"{'='*70}")


if __name__ == "__main__":
    import_qualitative_analyses()


