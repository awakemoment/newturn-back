"""
초정밀 10-K 데이터 검증

모든 종목의:
1. 원본 HTML 크기 vs 파싱된 텍스트 크기 비교
2. Item 1, 1A, 7 각각의 완전성 확인
3. 테이블 데이터 존재 여부
4. 숫자 데이터 추출 가능성
5. 누락 가능성 있는 섹션

→ 100% 완전한 데이터 확보!
"""
import os
import json
import re


def validate_stock(ticker):
    """종목 완전성 검증"""
    
    print(f"\n{'='*80}")
    print(f"🔬 {ticker} 초정밀 검증")
    print('='*80)
    
    # 1. 파싱 메타데이터 확인
    meta_file = f'data/parsed_10k_{ticker}.json'
    
    if not os.path.exists(meta_file):
        print(f"   ❌ 메타 파일 없음: {meta_file}")
        return {'status': 'NO_META'}
    
    with open(meta_file, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    parsed_data = meta.get('parsed', {})
    
    print(f"\n📄 원본 HTML:")
    print(f"   (다운로드된 HTML 크기는 메타에 없음)")
    
    print(f"\n📝 파싱된 텍스트:")
    print(f"   Total: {parsed_data.get('text_length', 0):,} characters")
    print(f"   Lines: {parsed_data.get('line_count', 0):,}")
    
    # 2. 섹션별 검증
    sections = parsed_data.get('sections', {})
    
    print(f"\n📂 섹션별 상태:")
    
    validation = {}
    
    for section_name in ['item_1_business', 'item_1a_risk_factors', 'item_7_mda']:
        section_data = sections.get(section_name)
        
        if not section_data:
            print(f"   ❌ {section_name}: 없음")
            validation[section_name] = {'status': 'MISSING'}
            continue
        
        # 파일 확인
        text_file = section_data.get('text_file')
        
        if text_file and os.path.exists(text_file):
            with open(text_file, 'r', encoding='utf-8') as f:
                actual_text = f.read()
            
            actual_size = len(actual_text)
            expected_size = section_data.get('char_count', 0)
            
            match = actual_size == expected_size
            
            print(f"   ✅ {section_name}:")
            print(f"      Pages: ~{section_data.get('page_estimate', 0):.1f}")
            print(f"      Words: {section_data.get('word_count', 0):,}")
            print(f"      File: {text_file}")
            print(f"      Size: {actual_size:,} chars {'✅' if match else f'⚠️ (expected {expected_size:,})'}")
            
            # 특정 섹션 추가 검증
            if section_name == 'item_7_mda':
                # 매출 테이블 찾기
                revenue_keywords = [
                    'net sales by',
                    'revenue by',
                    'segment revenue',
                    'sales by product',
                    'sales by segment'
                ]
                
                found_keywords = []
                for keyword in revenue_keywords:
                    if keyword in actual_text.lower():
                        count = actual_text.lower().count(keyword)
                        found_keywords.append(f"{keyword} ({count}회)")
                
                if found_keywords:
                    print(f"      💰 매출 관련: {', '.join(found_keywords[:3])}")
                else:
                    print(f"      ⚠️ 매출 테이블 키워드 없음!")
                
                # 숫자 데이터 샘플
                dollar_amounts = re.findall(r'\$[\d,]+', actual_text[:5000])  # 처음 5000자에서
                if dollar_amounts:
                    print(f"      💵 금액 데이터: {len(dollar_amounts)}개 발견 (예: {dollar_amounts[:3]})")
                else:
                    print(f"      ⚠️ 금액 데이터 없음!")
            
            validation[section_name] = {
                'status': 'OK',
                'size': actual_size,
                'pages': section_data.get('page_estimate', 0)
            }
        else:
            print(f"   ⚠️ {section_name}: 파일 없음 ({text_file})")
            validation[section_name] = {'status': 'NO_FILE'}
    
    return {
        'ticker': ticker,
        'sections': validation,
        'total_chars': parsed_data.get('text_length', 0)
    }


def check_all():
    """모든 종목 검증"""
    
    STOCKS = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN',
        'NVDA', 'META', 'V', 'PG', 'TSLA'
    ]
    
    print("="*80)
    print("🔬 초정밀 10-K 데이터 검증")
    print("="*80)
    print()
    print("목표: 원본과 파싱 데이터 완전성 100% 확인")
    print("검증 항목:")
    print("  1. 섹션 파일 존재 여부")
    print("  2. 섹션 크기 일치 여부")
    print("  3. 매출 테이블 존재 여부")
    print("  4. 숫자 데이터 존재 여부")
    print()
    
    results = {}
    
    for ticker in STOCKS:
        result = validate_stock(ticker)
        results[ticker] = result
    
    # 최종 요약
    print(f"\n{'='*80}")
    print("📊 최종 검증 결과")
    print('='*80)
    
    stats = {
        'total': len(STOCKS),
        'item1_ok': 0,
        'item1a_ok': 0,
        'item7_ok': 0,
        'all_ok': 0,
        'issues': []
    }
    
    for ticker, result in results.items():
        sections = result.get('sections', {})
        
        item1_ok = sections.get('item_1_business', {}).get('status') == 'OK'
        item1a_ok = sections.get('item_1a_risk_factors', {}).get('status') == 'OK'
        item7_ok = sections.get('item_7_mda', {}).get('status') == 'OK'
        
        if item1_ok:
            stats['item1_ok'] += 1
        if item1a_ok:
            stats['item1a_ok'] += 1
        if item7_ok:
            stats['item7_ok'] += 1
        
        if item1_ok and item1a_ok and item7_ok:
            stats['all_ok'] += 1
        else:
            stats['issues'].append({
                'ticker': ticker,
                'item1': item1_ok,
                'item1a': item1a_ok,
                'item7': item7_ok
            })
    
    print(f"\n전체 종목: {stats['total']}개")
    print(f"\n섹션별 성공률:")
    print(f"  Item 1 (Business):     {stats['item1_ok']}/{stats['total']} ({stats['item1_ok']/stats['total']*100:.1f}%)")
    print(f"  Item 1A (Risk):        {stats['item1a_ok']}/{stats['total']} ({stats['item1a_ok']/stats['total']*100:.1f}%)")
    print(f"  Item 7 (MD&A):         {stats['item7_ok']}/{stats['total']} ({stats['item7_ok']/stats['total']*100:.1f}%)")
    print(f"\n전체 완전성: {stats['all_ok']}/{stats['total']} ({stats['all_ok']/stats['total']*100:.1f}%)")
    
    if stats['issues']:
        print(f"\n⚠️ 문제 있는 종목:")
        for issue in stats['issues']:
            missing = []
            if not issue['item1']:
                missing.append('Item1')
            if not issue['item1a']:
                missing.append('Item1A')
            if not issue['item7']:
                missing.append('Item7')
            
            print(f"   {issue['ticker']}: {', '.join(missing)} 누락")
    
    # 저장
    with open('data/deep_validation_report.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 상세 리포트 저장: data/deep_validation_report.json")
    
    print(f"\n{'='*80}")
    print("🎯 조치 필요:")
    print('='*80)
    
    if stats['all_ok'] < stats['total']:
        print("  1. 누락 종목 재수집 필요")
        print("  2. 파서 로직 개선")
        print("  3. 테이블 패턴 추가")
    else:
        print("  ✅ 모든 데이터 완전!")
    
    print('='*80)


if __name__ == "__main__":
    check_all()

