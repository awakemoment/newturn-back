"""
JPM (금융) 10-K 파싱 테스트
금융 산업의 10-K 형식 파악
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ixbrl_parser import iXBRLParser

print("="*80)
print("🏦 JPM (금융) 10-K 파싱 테스트")
print("="*80)

parser = iXBRLParser()

# 1. 메타데이터
print("\n1️⃣ 메타데이터 수집...")
metadata = parser.get_latest_10k('JPM')

if metadata:
    print(f"   ✅ Filing Date: {metadata['filing_date']}")
    print(f"   ✅ Document: {metadata['primary_document']}")
    
    # 2. 다운로드
    print("\n2️⃣ HTML 다운로드...")
    html = parser.download_10k_html(metadata['document_url'])
    print(f"   ✅ Size: {len(html):,} bytes")
    
    # 3. 파싱
    print("\n3️⃣ 파싱...")
    parsed = parser.parse_ixbrl_10k(html)
    
    # 4. 결과 저장
    print("\n4️⃣ 저장...")
    parser.save_parsed_10k('JPM', metadata, parsed)
    
    # 5. 요약
    print(f"\n{'='*80}")
    print("📊 JPM 10-K 요약")
    print('='*80)
    sections = parsed.get('sections', {})
    for name, data in sections.items():
        if data:
            print(f"{name}:")
            print(f"   Pages: ~{data['page_estimate']:.1f}")
            print(f"   Words: {data['word_count']:,}")
    
    print(f"\n✅ JPM 파싱 완료!")
else:
    print("❌ 메타데이터 수집 실패")


