"""
TSLA 10-K 수집 (수정된 파서 사용)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ixbrl_parser import iXBRLParser

print("="*80)
print("🚗 TSLA 10-K 수집 (수정된 파서)")
print("="*80)

parser = iXBRLParser()

# TSLA 수집
metadata = parser.get_latest_10k('TSLA')

if metadata:
    print(f"✅ Filing: {metadata.get('filing_type', '10-K')} - {metadata['filing_date']}")
    
    # 다운로드
    html = parser.download_10k_html(metadata['document_url'])
    
    # 파싱
    parsed = parser.parse_ixbrl_10k(html)
    
    # 저장
    parser.save_parsed_10k('TSLA', metadata, parsed)
    
    print(f"\n🎉 TSLA 수집 완료!")
else:
    print("❌ TSLA 수집 실패")

