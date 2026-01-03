"""
나머지 종목 매출 테이블 수동 찾기

GOOGL, AMZN, V, PG, TSLA
각각의 Item 7에서 매출 테이블 위치 파악
"""
import re


def find_googl_revenue():
    """GOOGL 매출 찾기"""
    
    with open('data/section_GOOGL_item_7_mda.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    # "revenue" 포함 줄 찾기
    lines = text.split('\n')
    
    print("="*80)
    print("🔍 GOOGL 매출 테이블 찾기")
    print("="*80)
    
    for i, line in enumerate(lines):
        # 숫자가 있는 revenue 줄
        if 'revenue' in line.lower() and ('$' in line or any(c.isdigit() for c in line)):
            if len(line.strip()) > 10:
                print(f"Line {i}: {line.strip()[:100]}")
        
        # "Google Services" + 숫자
        if 'google services' in line.lower() and any(c.isdigit() for c in line):
            print(f"Line {i} [Services]: {line.strip()[:100]}")
        
        # "Google Cloud" + 숫자  
        if 'google cloud' in line.lower() and any(c.isdigit() for c in line):
            print(f"Line {i} [Cloud]: {line.strip()[:100]}")
        
        # 특정 패턴 찾기
        if re.search(r'(Google Services|Google Cloud).*\$.*\d{3},\d{3}', line, re.IGNORECASE):
            print(f"Line {i} [MATCH]: {line.strip()}")


def find_amzn_revenue():
    """AMZN 매출 찾기"""
    
    with open('data/section_AMZN_item_7_mda.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    lines = text.split('\n')
    
    print("\n" + "="*80)
    print("🔍 AMZN 매출 테이블 찾기")
    print("="*80)
    
    for i, line in enumerate(lines):
        # AWS, North America, International
        if any(kw in line for kw in ['AWS', 'North America segment', 'International segment']):
            if any(c.isdigit() for c in line):
                print(f"Line {i}: {line.strip()[:100]}")


def find_v_revenue():
    """Visa 매출 찾기"""
    
    with open('data/section_V_item_7_mda.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    lines = text.split('\n')
    
    print("\n" + "="*80)
    print("🔍 VISA 매출 테이블 찾기")
    print("="*80)
    
    for i, line in enumerate(lines):
        # Service revenues, Data processing revenues
        if any(kw in line for kw in ['Service revenues', 'Data processing revenues', 'International transaction revenues']):
            if any(c.isdigit() for c in line):
                print(f"Line {i}: {line.strip()[:100]}")


if __name__ == "__main__":
    find_googl_revenue()
    find_amzn_revenue()
    find_v_revenue()
    
    print("\n" + "="*80)
    print("💡 위 결과를 보고 정확한 라인 번호 확인 후")
    print("   실제 매출 숫자 추출하겠습니다!")
    print("="*80)

