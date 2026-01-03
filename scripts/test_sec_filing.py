"""
SEC 10-K 수집 및 파싱 테스트

목표: AAPL의 최신 10-K를 가져와서 주요 섹션 추출
"""
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import time


class SECFilingCollector:
    """SEC EDGAR에서 10-K 수집"""
    
    BASE_URL = "https://www.sec.gov"
    
    def __init__(self):
        # SEC는 User-Agent 필수!
        self.headers = {
            'User-Agent': 'Newturn AI Investment newturn@example.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
    
    def get_cik(self, ticker):
        """티커 → CIK 변환"""
        # SEC의 company_tickers.json 사용
        url = "https://www.sec.gov/files/company_tickers.json"
        
        response = requests.get(url, headers=self.headers)
        time.sleep(0.1)  # Rate limit 준수
        
        data = response.json()
        
        for key, company in data.items():
            if company['ticker'].upper() == ticker.upper():
                cik = str(company['cik_str']).zfill(10)  # 10자리로
                return cik
        
        return None
    
    def get_latest_10k_url(self, ticker):
        """최신 10-K 문서 URL 찾기"""
        cik = self.get_cik(ticker)
        
        if not cik:
            print(f"❌ CIK not found for {ticker}")
            return None
        
        print(f"✅ {ticker} CIK: {cik}")
        
        # Filing 검색
        url = f"{self.BASE_URL}/cgi-bin/browse-edgar"
        params = {
            'action': 'getcompany',
            'CIK': cik,
            'type': '10-K',
            'dateb': '',
            'owner': 'exclude',
            'count': '1',
            'search_text': ''
        }
        
        response = requests.get(url, params=params, headers=self.headers)
        time.sleep(0.1)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Documents 버튼 찾기
        doc_button = soup.find('a', {'id': 'documentsbutton'})
        
        if not doc_button:
            print("❌ No 10-K found")
            return None
        
        doc_url = self.BASE_URL + doc_button['href']
        print(f"✅ 10-K Documents page: {doc_url}")
        
        # Documents 페이지에서 실제 HTML 파일 찾기
        response = requests.get(doc_url, headers=self.headers)
        time.sleep(0.1)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Table에서 10-K HTML 찾기
        table = soup.find('table', {'class': 'tableFile'})
        
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 4:
                    doc_type = cells[3].get_text(strip=True)
                    description = cells[1].get_text(strip=True) if len(cells) > 1 else ''
                    
                    # 일반 HTML 문서 찾기 (iXBRL 제외)
                    if doc_type == '10-K' and 'htm' in description.lower() and 'ix?' not in str(cells[2]):
                        link = cells[2].find('a')
                        if link and 'ix?' not in link.get('href', ''):
                            filing_url = self.BASE_URL + link['href']
                            print(f"✅ 10-K HTML: {filing_url}")
                            return filing_url
            
            # 일반 HTML 못 찾으면 첫 번째 10-K
            print("⚠️ No plain HTML found, trying first 10-K...")
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 4:
                    doc_type = cells[3].get_text(strip=True)
                    if doc_type == '10-K':
                        link = cells[2].find('a')
                        if link:
                            filing_url = self.BASE_URL + link['href']
                            print(f"✅ 10-K (any format): {filing_url}")
                            return filing_url
        
        return None
    
    def get_latest_10k_txt(self, ticker):
        """최신 10-K 텍스트 파일 URL 찾기"""
        cik = self.get_cik(ticker)
        
        if not cik:
            return None
        
        # Filing 검색
        url = f"{self.BASE_URL}/cgi-bin/browse-edgar"
        params = {
            'action': 'getcompany',
            'CIK': cik,
            'type': '10-K',
            'dateb': '',
            'owner': 'exclude',
            'count': '1',
        }
        
        response = requests.get(url, params=params, headers=self.headers)
        time.sleep(0.1)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Documents 버튼 찾기
        doc_button = soup.find('a', {'id': 'documentsbutton'})
        
        if not doc_button:
            return None
        
        # Documents 페이지 URL에서 accession number 추출
        doc_path = doc_button['href']
        # /Archives/edgar/data/320193/000032019325000079/0000320193-25-000079-index.htm
        
        # accession number 추출 (0000320193-25-000079)
        match = re.search(r'/(\d+-\d+-\d+)-index\.htm', doc_path)
        if match:
            accession = match.group(1)
            # 텍스트 파일 URL 생성
            txt_url = f"{self.BASE_URL}/cgi-bin/viewer?action=view&cik={cik}&accession_number={accession}&xbrl_type=v"
            print(f"✅ 10-K TXT: {txt_url}")
            return txt_url
        
        return None
    
    def download_10k(self, ticker):
        """10-K 텍스트 다운로드"""
        # 먼저 텍스트 버전 시도
        url = self.get_latest_10k_txt(ticker)
        
        if url:
            print(f"\n📥 Downloading 10-K (TXT)...")
            response = requests.get(url, headers=self.headers)
            time.sleep(0.1)
            
            print(f"✅ Downloaded {len(response.text):,} characters")
            return response.text
        
        # 안 되면 HTML 버전
        url = self.get_latest_10k_url(ticker)
        
        if not url:
            return None
        
        print(f"\n📥 Downloading 10-K (HTML)...")
        response = requests.get(url, headers=self.headers)
        time.sleep(0.1)
        
        print(f"✅ Downloaded {len(response.text):,} characters")
        
        return response.text
    
    def extract_text_clean(self, html):
        """HTML → 깨끗한 텍스트"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Script, style 태그 제거
        for tag in soup(['script', 'style', 'meta', 'link']):
            tag.decompose()
        
        # 텍스트 추출
        text = soup.get_text(separator=' ', strip=True)
        
        # 연속 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def find_section(self, text, item_name, next_item_name=None):
        """특정 Item 섹션 찾기"""
        
        # Item 1, Item 1A 같은 패턴들
        patterns = [
            f"Item {item_name}[.:]",
            f"ITEM {item_name}[.:]",
            f"Item {item_name} ",
            f"ITEM {item_name} ",
        ]
        
        start_pos = None
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                start_pos = match.start()
                print(f"✅ Found '{item_name}' at position {start_pos}")
                break
        
        if not start_pos:
            print(f"⚠️ '{item_name}' not found")
            return None
        
        # 끝 위치 찾기
        if next_item_name:
            next_patterns = [
                f"Item {next_item_name}[.:]",
                f"ITEM {next_item_name}[.:]",
            ]
            
            end_pos = None
            for pattern in next_patterns:
                match = re.search(pattern, text[start_pos+100:], re.IGNORECASE)
                if match:
                    end_pos = start_pos + 100 + match.start()
                    break
            
            if end_pos:
                section = text[start_pos:end_pos]
            else:
                # 다음 Item 못 찾으면 15000자만
                section = text[start_pos:start_pos+15000]
        else:
            section = text[start_pos:start_pos+15000]
        
        return section.strip()
    
    def extract_key_sections(self, html):
        """주요 섹션 추출"""
        
        text = self.extract_text_clean(html)
        print(f"\n📄 Total text length: {len(text):,} characters")
        
        sections = {}
        
        # Item 1: Business
        print("\n🔍 Extracting Item 1: Business...")
        business = self.find_section(text, "1", "1A")
        if business:
            sections['business'] = business[:10000]  # 처음 10000자
            print(f"   Length: {len(business):,} chars")
        
        # Item 1A: Risk Factors
        print("\n🔍 Extracting Item 1A: Risk Factors...")
        risks = self.find_section(text, "1A", "1B")
        if risks:
            sections['risk_factors'] = risks[:15000]
            print(f"   Length: {len(risks):,} chars")
        
        # Item 7: MD&A
        print("\n🔍 Extracting Item 7: MD&A...")
        mda = self.find_section(text, "7", "7A")
        if mda:
            sections['mda'] = mda[:10000]
            print(f"   Length: {len(mda):,} chars")
        
        return sections


# 테스트 실행
if __name__ == "__main__":
    print("="*60)
    print("🚀 SEC 10-K 수집 테스트")
    print("="*60)
    
    collector = SECFilingCollector()
    
    # AAPL 테스트
    ticker = "AAPL"
    print(f"\n📊 Testing with {ticker}")
    
    # 10-K 다운로드
    html = collector.download_10k(ticker)
    
    if html:
        # 주요 섹션 추출
        sections = collector.extract_key_sections(html)
        
        # 결과 저장
        output_file = f"business/newturn-back/data/sec_{ticker}_10k.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'ticker': ticker,
                'collected_at': datetime.now().isoformat(),
                'sections': sections
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved to {output_file}")
        print(f"\n📋 Sections extracted:")
        for key, value in sections.items():
            print(f"   - {key}: {len(value):,} chars")
    else:
        print("❌ Failed to download 10-K")

