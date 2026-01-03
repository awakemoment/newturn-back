"""
모든 종목 10-K 데이터 완전성 검증

목표:
1. 각 종목의 Item 7 (MD&A)에서 매출 테이블 찾기
2. 제품별/세그먼트별/지역별 매출 확인
3. 누락된 데이터 발견
4. 재파싱 필요 항목 리스트업

산업별 특징:
- Tech: 제품별 (iPhone, Mac, iPad...)
- Finance: 세그먼트별 (Consumer Banking, Investment Banking...)
- Healthcare: 부문별 (Pharma, Medical Devices...)
- Energy: 부문별 (Upstream, Downstream...)
- Consumer: 브랜드별/지역별
"""
import os
import json
import re


STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 
    'NVDA', 'META', 'V', 'PG',
    'TSLA',  # 추가
]


def find_revenue_tables(ticker):
    """종목별 매출 테이블 위치 찾기"""
    
    filename = f'data/section_{ticker}_item_7_mda.txt'
    
    if not os.path.exists(filename):
        return None
    
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 매출 관련 테이블 패턴
    patterns = [
        r'net sales by category',
        r'net sales by segment',
        r'revenue by product',
        r'revenue by segment',
        r'segment information',
        r'disaggregation of revenue',
        r'revenue from contracts',
    ]
    
    found_tables = []
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            pos = match.start()
            # 전후 500자 추출
            context = text[max(0, pos-200):min(len(text), pos+800)]
            
            found_tables.append({
                'pattern': pattern,
                'position': pos,
                'context': context[:500]  # 처음 500자만
            })
    
    return {
        'ticker': ticker,
        'file_exists': True,
        'file_size': len(text),
        'tables_found': len(found_tables),
        'tables': found_tables[:3]  # 처음 3개만
    }


def check_all_stocks():
    """모든 종목 검증"""
    
    print("="*80)
    print("🔍 전체 종목 10-K 데이터 완전성 검증")
    print("="*80)
    print()
    print("목표: 매출 테이블이 제대로 파싱되었는지 확인")
    print()
    
    results = {}
    
    for ticker in STOCKS:
        print(f"\n{'='*80}")
        print(f"📊 {ticker} 검증 중...")
        print('-'*80)
        
        result = find_revenue_tables(ticker)
        
        if not result:
            print(f"   ❌ Item 7 파일 없음")
            results[ticker] = {'status': 'NO_FILE'}
            continue
        
        print(f"   ✅ File size: {result['file_size']:,} bytes")
        print(f"   ✅ Tables found: {result['tables_found']}개")
        
        if result['tables_found'] == 0:
            print(f"   ⚠️ 매출 테이블을 찾지 못했습니다!")
        else:
            for i, table in enumerate(result['tables'], 1):
                print(f"\n   Table #{i}:")
                print(f"      Pattern: '{table['pattern']}'")
                print(f"      Position: {table['position']:,}")
                print(f"      Preview: {table['context'][:200]}...")
        
        results[ticker] = result
    
    # 요약
    print(f"\n{'='*80}")
    print("📊 검증 결과 요약")
    print('='*80)
    
    total = len(STOCKS)
    with_tables = len([r for r in results.values() if r.get('tables_found', 0) > 0])
    no_tables = total - with_tables
    
    print(f"\n총 종목: {total}개")
    print(f"✅ 테이블 발견: {with_tables}개")
    print(f"⚠️ 테이블 없음: {no_tables}개")
    
    if no_tables > 0:
        print(f"\n⚠️ 테이블 못 찾은 종목:")
        for ticker, result in results.items():
            if result.get('tables_found', 0) == 0:
                print(f"   - {ticker}")
    
    # 저장
    with open('data/validation_report.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 저장: data/validation_report.json")
    
    print(f"\n{'='*80}")
    print("🎯 다음 단계:")
    print("="*80)
    print("  1. 테이블 못 찾은 종목 → 수동 확인")
    print("  2. 각 산업별 테이블 형식 파악")
    print("  3. 범용 테이블 파서 개발")
    print("  4. 전체 재파싱")
    print("="*80)
    
    return results


if __name__ == "__main__":
    check_all_stocks()

