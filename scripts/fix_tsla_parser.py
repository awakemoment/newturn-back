"""
TSLA 10-K 수집 수정

문제: 10-K/A는 수정본이라 전체 내용이 없을 수 있음
해결: 10-K (원본) 우선, 없으면 10-K/A
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from bs4 import BeautifulSoup
import time
from ixbrl_parser import iXBRLParser


def get_tsla_original_10k():
    """TSLA 원본 10-K 찾기 (10-K/A 제외)"""
    
    BASE_URL = "https://www.sec.gov"
    headers = {
        'User-Agent': 'Newturn Investment Platform contact@newturn.ai',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }
    
    cik = "0001318605"
    ticker = "TSLA"
    
    print("="*80)
    print("🔍 TSLA 원본 10-K 찾기")
    print("="*80)
    
    # 최근 10개 Filing 확인
    url = f"{BASE_URL}/cgi-bin/browse-edgar"
    params = {
        'action': 'getcompany',
        'CIK': cik,
        'type': '10-K',
        'dateb': '',
        'owner': 'exclude',
        'count': '10',  # 최근 10개
    }
    
    response = requests.get(url, params=params, headers=headers)
    time.sleep(0.11)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', class_='tableFile2')
    
    if not table:
        print("❌ No table")
        return None
    
    rows = table.find_all('tr')[1:]
    
    print(f"\n최근 10개 Filing:")
    
    original_10k = None
    
    for i, row in enumerate(rows, 1):
        cells = row.find_all('td')
        filing_type = cells[0].text.strip()
        filing_date = cells[3].text.strip()
        
        print(f"  {i}. {filing_type:10s} - {filing_date}")
        
        # 10-K (원본) 우선 선택
        if filing_type == '10-K' and not original_10k:
            original_10k = row
            print(f"     ✅ 원본 10-K 발견!")
    
    if not original_10k:
        print("\n⚠️ 원본 10-K 없음. 10-K/A 사용...")
        # 10-K/A라도 사용
        for row in rows:
            cells = row.find_all('td')
            filing_type = cells[0].text.strip()
            if filing_type == '10-K/A':
                original_10k = row
                print(f"  10-K/A 사용: {cells[3].text.strip()}")
                break
    
    if not original_10k:
        print("❌ 10-K도 10-K/A도 없음")
        return None
    
    # Documents 버튼
    doc_button = original_10k.find('a', {'id': 'documentsbutton'})
    if not doc_button:
        print("❌ No documents button")
        return None
    
    filing_date = original_10k.find_all('td')[3].text.strip()
    documents_url = BASE_URL + doc_button['href']
    
    print(f"\n✅ Documents: {documents_url}")
    
    # Documents 페이지에서 HTML 파일 찾기
    response2 = requests.get(documents_url, headers=headers)
    time.sleep(0.11)
    
    soup2 = BeautifulSoup(response2.content, 'html.parser')
    table2 = soup2.find('table', class_='tableFile')
    
    if not table2:
        print("❌ No documents table")
        return None
    
    # 10-K 문서 찾기
    for row in table2.find_all('tr')[1:]:
        cells = row.find_all('td')
        if len(cells) >= 4:
            doc_type = cells[3].text.strip()
            
            if doc_type in ['10-K', '10-K/A']:
                link = cells[2].find('a')
                if link:
                    href = link.get('href', '')
                    
                    if 'ix?doc=' in href:
                        actual_path = href.split('ix?doc=')[1]
                        doc_url = BASE_URL + actual_path
                    else:
                        doc_url = BASE_URL + href
                    
                    print(f"✅ 10-K URL: {doc_url}")
                    
                    return {
                        'ticker': ticker,
                        'cik': cik,
                        'filing_date': filing_date,
                        'document_url': doc_url,
                    }
    
    return None


if __name__ == "__main__":
    metadata = get_tsla_original_10k()
    
    if metadata:
        print(f"\n{'='*80}")
        print("📥 TSLA 10-K 다운로드 및 파싱")
        print('='*80)
        
        parser = iXBRLParser()
        
        # 다운로드
        html = parser.download_10k_html(metadata['document_url'])
        
        # 파싱
        parsed = parser.parse_ixbrl_10k(html)
        
        # 저장
        parser.save_parsed_10k('TSLA', metadata, parsed)
        
        print(f"\n🎉 TSLA 10-K 완전 수집 성공!")
    else:
        print("\n❌ TSLA 10-K 찾기 실패")

