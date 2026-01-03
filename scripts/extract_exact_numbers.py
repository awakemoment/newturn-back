"""
정확한 매출 숫자 추출

각 종목의 Item 7에서 숫자 테이블 찾기
"""
import re


def extract_googl_revenue():
    """GOOGL 세그먼트 매출 추출"""
    
    with open('data/section_GOOGL_item_7_mda.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("="*80)
    print("📊 GOOGL 매출 추출")
    print("="*80)
    
    # "segment results" 또는 "consolidated revenues" 근처 찾기
    for i in range(len(lines)):
        line = lines[i]
        
        # 세그먼트 결과 테이블 찾기
        if 'segment results' in line.lower() or 'consolidated revenues' in line.lower():
            print(f"\nLine {i}: {line.strip()}")
            
            # 다음 50줄 확인
            for j in range(i, min(i+50, len(lines))):
                next_line = lines[j]
                
                # Google Services, Google Cloud, Other Bets + 숫자
                if any(kw in next_line for kw in ['Google Services', 'Google Cloud', 'Other Bets']):
                    # 그 줄 + 다음 5줄 출력 (테이블 구조)
                    print(f"\n  Found at line {j}:")
                    for k in range(j, min(j+10, len(lines))):
                        print(f"    {k}: {lines[k].rstrip()}")
                    break


def extract_amzn_revenue():
    """AMZN 세그먼트 매출 추출"""
    
    with open('data/section_AMZN_item_7_mda.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("\n" + "="*80)
    print("📊 AMZN 매출 추출")
    print("="*80)
    
    # "North America" + "International" + "AWS" 동시 나오는 테이블
    for i in range(len(lines)):
        line = lines[i]
        
        if 'segment information' in line.lower() or 'net sales' in line.lower():
            # 주변 체크
            context = ''.join(lines[max(0, i-2):min(i+30, len(lines))])
            
            if 'North America' in context and 'AWS' in context and '$' in context:
                print(f"\nLine {i}: {line.strip()}")
                print("\n  Context:")
                for j in range(max(0, i-2), min(i+30, len(lines))):
                    if any(kw in lines[j] for kw in ['North America', 'International', 'AWS', '$']):
                        print(f"    {j}: {lines[j].rstrip()}")


def extract_v_revenue():
    """VISA 매출 추출"""
    
    with open('data/section_V_item_7_mda.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("\n" + "="*80)
    print("📊 VISA 매출 추출")
    print("="*80)
    
    # Visa는 제품별: Service revenues, Data processing, International transaction, Other
    for i in range(len(lines)):
        line = lines[i]
        
        # Operating revenues 테이블
        if 'operating revenues' in line.lower() or 'net revenues' in line.lower():
            context = ''.join(lines[i:min(i+40, len(lines))])
            
            if 'service revenues' in context.lower() and '$' in context:
                print(f"\nLine {i}: {line.strip()}")
                print("\n  Context:")
                for j in range(i, min(i+40, len(lines))):
                    if '$' in lines[j] or 'revenues' in lines[j].lower():
                        print(f"    {j}: {lines[j].rstrip()[:120]}")


if __name__ == "__main__":
    extract_googl_revenue()
    extract_amzn_revenue()
    extract_v_revenue()
    
    print("\n" + "="*80)
    print("✅ 테이블 위치 파악 완료!")
    print("   다음: 정확한 숫자 추출")
    print("="*80)

