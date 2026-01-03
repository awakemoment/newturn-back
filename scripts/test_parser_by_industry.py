"""
산업별 10-K 파싱 테스트

목표: 
- 6개 산업별로 대표 종목 2개씩 샘플링
- 각각 10-K 수집 및 파싱 시도
- 실패 케이스 분석
- 범용 파서 개발

산업 분류:
1. Technology: AAPL, MSFT
2. Finance: JPM, BAC (Bank of America)
3. Healthcare: JNJ, PFE (Pfizer)
4. Energy: XOM, CVX
5. Consumer: KO, WMT
6. Industrial: CAT (Caterpillar), BA (Boeing)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ixbrl_parser import iXBRLParser
import json
import time


# 산업별 샘플 종목
INDUSTRY_SAMPLES = {
    'Technology': ['AAPL', 'MSFT'],
    'Finance': ['JPM', 'BAC'],
    'Healthcare': ['JNJ', 'PFE'],
    'Energy': ['XOM', 'CVX'],
    'Consumer': ['KO', 'WMT'],
    'Industrial': ['CAT', 'BA'],
}


def test_all_industries():
    """모든 산업 샘플 테스트"""
    
    print("="*80)
    print("🧪 산업별 10-K 파싱 테스트")
    print("="*80)
    print()
    print("목표: 다양한 산업의 10-K 형식을 파악하여 범용 파서 개발")
    print()
    print("="*80)
    
    parser = iXBRLParser()
    
    results = {}
    
    for industry, tickers in INDUSTRY_SAMPLES.items():
        print(f"\n{'='*80}")
        print(f"🏭 {industry} Industry")
        print('='*80)
        
        industry_results = []
        
        for ticker in tickers:
            print(f"\n📊 Testing {ticker}...")
            print("-"*80)
            
            try:
                # 1. 메타데이터 가져오기
                metadata = parser.get_latest_10k(ticker)
                
                if not metadata:
                    print(f"   ❌ Failed to get metadata")
                    industry_results.append({
                        'ticker': ticker,
                        'status': 'FAILED',
                        'reason': 'No metadata'
                    })
                    continue
                
                # 2. HTML 다운로드
                html = parser.download_10k_html(metadata['document_url'])
                
                if not html or len(html) < 1000:
                    print(f"   ❌ Failed to download or file too small")
                    industry_results.append({
                        'ticker': ticker,
                        'status': 'FAILED',
                        'reason': 'Download failed'
                    })
                    continue
                
                # 3. 파싱
                parsed = parser.parse_ixbrl_10k(html)
                
                # 4. 결과 분석
                sections = parsed.get('sections', {})
                
                result = {
                    'ticker': ticker,
                    'status': 'SUCCESS',
                    'filing_date': metadata['filing_date'],
                    'text_length': parsed['text_length'],
                    'line_count': parsed['line_count'],
                    'sections_found': list(sections.keys()),
                    'sections_count': len(sections),
                }
                
                # 섹션별 통계
                for section_name, section_data in sections.items():
                    if section_data:
                        result[f'{section_name}_pages'] = section_data['page_estimate']
                        result[f'{section_name}_words'] = section_data['word_count']
                
                industry_results.append(result)
                
                # 결과 출력
                print(f"\n   ✅ SUCCESS")
                print(f"      Filing Date: {metadata['filing_date']}")
                print(f"      Total Text: {parsed['text_length']:,} chars")
                print(f"      Sections: {len(sections)}")
                
                for section_name, section_data in sections.items():
                    if section_data:
                        print(f"         - {section_name}: ~{section_data['page_estimate']:.1f} pages")
                
                # Rate limit
                time.sleep(0.2)
                
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                industry_results.append({
                    'ticker': ticker,
                    'status': 'ERROR',
                    'error': str(e)
                })
                import traceback
                traceback.print_exc()
        
        results[industry] = industry_results
    
    # 최종 요약
    print(f"\n{'='*80}")
    print("📊 최종 결과 요약")
    print('='*80)
    
    total_tested = 0
    total_success = 0
    total_failed = 0
    
    for industry, industry_results in results.items():
        success = len([r for r in industry_results if r.get('status') == 'SUCCESS'])
        failed = len([r for r in industry_results if r.get('status') != 'SUCCESS'])
        
        total_tested += len(industry_results)
        total_success += success
        total_failed += failed
        
        print(f"\n{industry}:")
        print(f"   Success: {success}/{len(industry_results)}")
        
        for result in industry_results:
            status_icon = "✅" if result.get('status') == 'SUCCESS' else "❌"
            print(f"   {status_icon} {result['ticker']}: {result.get('status')}")
    
    print(f"\n{'='*80}")
    print(f"총 테스트: {total_tested}개")
    print(f"✅ 성공: {total_success}개 ({total_success/total_tested*100:.1f}%)")
    print(f"❌ 실패: {total_failed}개")
    print('='*80)
    
    # 결과 저장
    with open('data/parser_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 결과 저장: data/parser_test_results.json")
    
    return results


if __name__ == "__main__":
    results = test_all_industries()


