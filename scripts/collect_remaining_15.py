"""
나머지 15개 주요 종목 10-K 수집
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ixbrl_parser import iXBRLParser
import time

# Top 15 종목
TOP_15 = [
    'AAPL',   # ✅ 완료
    'MSFT',   # ✅ 완료
    'GOOGL',
    'AMZN',
    'NVDA',
    'META',
    'TSLA',
    'JPM',    # ✅ 완료
    'V',
    'JNJ',    # ✅ 완료
    'WMT',    # ✅ 완료
    'PG',
    'XOM',    # ✅ 완료
    'CVX',    # ✅ 완료
    'KO',     # ✅ 완료
]

ALREADY_COLLECTED = ['AAPL', 'MSFT', 'JPM', 'JNJ', 'WMT', 'XOM', 'CVX', 'KO']
REMAINING = [t for t in TOP_15 if t not in ALREADY_COLLECTED]

print("="*80)
print("📥 나머지 종목 10-K 수집")
print("="*80)
print(f"\n이미 수집: {len(ALREADY_COLLECTED)}개")
print(f"남은 종목: {len(REMAINING)}개")
print(f"목록: {', '.join(REMAINING)}")
print()

parser = iXBRLParser()

for i, ticker in enumerate(REMAINING, 1):
    print(f"\n{'='*80}")
    print(f"[{i}/{len(REMAINING)}] {ticker}")
    print('='*80)
    
    try:
        # 메타데이터
        metadata = parser.get_latest_10k(ticker)
        
        if not metadata:
            print(f"❌ {ticker} metadata failed")
            continue
        
        # 다운로드
        html = parser.download_10k_html(metadata['document_url'])
        
        if not html:
            print(f"❌ {ticker} download failed")
            continue
        
        # 파싱
        parsed = parser.parse_ixbrl_10k(html)
        
        # 저장
        parser.save_parsed_10k(ticker, metadata, parsed)
        
        print(f"✅ {ticker} 완료!")
        
        # Rate limit
        time.sleep(0.2)
        
    except Exception as e:
        print(f"❌ {ticker} 오류: {e}")
        import traceback
        traceback.print_exc()
        continue

print(f"\n{'='*80}")
print("🎉 전체 15개 종목 수집 완료!")
print('='*80)

