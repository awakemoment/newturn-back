"""
TSLA 파싱 실패 원인 분석 및 해결

목표: TSLA를 포함한 모든 종목 100% 수집!
"""
import requests
from bs4 import BeautifulSoup
import time
import json


def debug_tsla():
    """TSLA 10-K 수집 디버깅"""
    
    BASE_URL = "https://www.sec.gov"
    headers = {
        'User-Agent': 'Newturn Investment Platform contact@newturn.ai',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }
    
    ticker = "TSLA"
    
    print("="*80)
    print(f"🔍 {ticker} 디버깅")
    print("="*80)
    
    # 1. CIK 확인
    print("\n1️⃣ CIK 확인...")
    cik_url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(cik_url, headers=headers)
    time.sleep(0.11)
    
    data = response.json()
    cik = None
    
    for key, company in data.items():
        if company['ticker'].upper() == ticker:
            cik = str(company['cik_str']).zfill(10)
            print(f"✅ CIK: {cik}")
            break
    
    if not cik:
        print("❌ CIK not found")
        return
    
    # 2. 10-K 검색
    print("\n2️⃣ 10-K 검색...")
    url = f"{BASE_URL}/cgi-bin/browse-edgar"
    params = {
        'action': 'getcompany',
        'CIK': cik,
        'type': '10-K',
        'dateb': '',
        'owner': 'exclude',
        'count': '3',  # 최근 3개 확인
    }
    
    response = requests.get(url, params=params, headers=headers)
    time.sleep(0.11)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Filing table 확인
    table = soup.find('table', class_='tableFile2')
    
    if not table:
        print("❌ No filing table")
        return
    
    rows = table.find_all('tr')[1:]  # Skip header
    
    print(f"✅ Found {len(rows)} filings:")
    
    for i, row in enumerate(rows[:3], 1):
        cells = row.find_all('td')
        filing_type = cells[0].text.strip()
        filing_date = cells[3].text.strip()
        
        print(f"\n   Filing #{i}:")
        print(f"     Type: {filing_type}")
        print(f"     Date: {filing_date}")
        
        # Documents 버튼
        doc_button = row.find('a', {'id': 'documentsbutton'})
        
        if doc_button:
            doc_url = BASE_URL + doc_button['href']
            print(f"     Documents: {doc_url}")
            
            # Documents 페이지 확인
            response2 = requests.get(doc_url, headers=headers)
            time.sleep(0.11)
            
            soup2 = BeautifulSoup(response2.content, 'html.parser')
            table2 = soup2.find('table', class_='tableFile')
            
            if table2:
                doc_rows = table2.find_all('tr')[1:]
                print(f"     Documents found: {len(doc_rows)}")
                
                # 10-K 문서 찾기
                for doc_row in doc_rows[:5]:  # 처음 5개만
                    doc_cells = doc_row.find_all('td')
                    if len(doc_cells) >= 4:
                        seq = doc_cells[0].text.strip()
                        description = doc_cells[1].text.strip()
                        doc_type = doc_cells[3].text.strip()
                        
                        link = doc_cells[2].find('a')
                        if link:
                            href = link.get('href', '')
                            filename = link.text.strip()
                            
                            print(f"        - [{seq}] {description[:40]} ({doc_type})")
                            print(f"          File: {filename}")
                            print(f"          Href: {href[:80]}...")
                            
                            # 10-K인지 확인
                            if doc_type == '10-K' or '10-K' in description:
                                print(f"          ✅ This is 10-K!")
                                
                                # URL 생성
                                if 'ix?doc=' in href:
                                    actual_path = href.split('ix?doc=')[1]
                                    final_url = BASE_URL + actual_path
                                else:
                                    final_url = BASE_URL + href
                                
                                print(f"          Final URL: {final_url}")
                                
                                # 다운로드 시도
                                print(f"          📥 Trying to download...")
                                try:
                                    response3 = requests.get(final_url, headers=headers, timeout=30)
                                    time.sleep(0.11)
                                    
                                    if response3.status_code == 200:
                                        size = len(response3.text)
                                        print(f"          ✅ Downloaded: {size:,} bytes")
                                        
                                        # 간단한 파싱 테스트
                                        if 'Item 1' in response3.text or 'ITEM 1' in response3.text:
                                            print(f"          ✅ Contains 'Item 1' - Likely valid!")
                                        else:
                                            print(f"          ⚠️ No 'Item 1' found")
                                        
                                        return {
                                            'success': True,
                                            'url': final_url,
                                            'size': size
                                        }
                                    else:
                                        print(f"          ❌ Status: {response3.status_code}")
                                except Exception as e:
                                    print(f"          ❌ Error: {e}")
            else:
                print(f"     ⚠️ No document table")
        else:
            print(f"     ⚠️ No documents button")
    
    return None


if __name__ == "__main__":
    result = debug_tsla()
    
    if result:
        print(f"\n{'='*80}")
        print("✅ TSLA 10-K 수집 가능!")
        print(f"URL: {result['url']}")
        print(f"Size: {result['size']:,} bytes")
        print("="*80)
    else:
        print(f"\n{'='*80}")
        print("❌ TSLA 10-K 수집 실패 - 추가 조사 필요")
        print("="*80)

