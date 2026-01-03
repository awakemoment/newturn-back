"""
완전한 10-K 사업보고서 수집 및 파싱

목표: 
- 전체 10-K HTML 다운로드 (100-300 페이지)
- Item별 섹션 완전 추출
- 테이블 데이터 파싱
- 구조화된 JSON 저장

이것이 뉴턴의 핵심 차별화!
"""
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import time
from urllib.parse import urljoin


class Full10KCollector:
    """완전한 10-K 수집기"""
    
    BASE_URL = "https://www.sec.gov"
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Newturn Investment Platform contact@newturn.ai',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
    
    def get_cik(self, ticker):
        """티커 → CIK"""
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, headers=self.headers)
        time.sleep(0.1)
        
        data = response.json()
        for key, company in data.items():
            if company['ticker'].upper() == ticker.upper():
                return str(company['cik_str']).zfill(10)
        return None
    
    def get_latest_10k_filing(self, ticker):
        """최신 10-K Filing 정보 가져오기"""
        cik = self.get_cik(ticker)
        if not cik:
            return None
        
        print(f"✅ {ticker} CIK: {cik}")
        
        # Filing 검색
        # 2023년 이전 10-K (일반 HTML 형식)
        url = f"{self.BASE_URL}/cgi-bin/browse-edgar"
        params = {
            'action': 'getcompany',
            'CIK': cik,
            'type': '10-K',
            'dateb': '20231231',  # 2023년 이전만 (일반 HTML)
            'owner': 'exclude',
            'count': '1',
        }
        
        response = requests.get(url, params=params, headers=self.headers)
        time.sleep(0.1)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Filing date
        table = soup.find('table', class_='tableFile2')
        if table:
            rows = table.find_all('tr')[1:]  # Skip header
            if rows:
                cells = rows[0].find_all('td')
                filing_date = cells[3].text.strip()
                print(f"✅ Filing Date: {filing_date}")
        
        # Documents 페이지
        doc_button = soup.find('a', {'id': 'documentsbutton'})
        if not doc_button:
            return None
        
        doc_url = self.BASE_URL + doc_button['href']
        print(f"✅ Documents: {doc_url}")
        
        return {
            'cik': cik,
            'filing_date': filing_date,
            'documents_url': doc_url
        }
    
    def find_10k_htm_file(self, documents_url):
        """10-K 메인 HTML 파일 찾기"""
        response = requests.get(documents_url, headers=self.headers)
        time.sleep(0.1)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', class_='tableFile')
        
        if not table:
            print("❌ No documents table found")
            return None
        
        # 우선순위:
        # 1. 일반 HTML (*.htm, not ix?)
        # 2. 가장 큰 파일
        
        candidates = []
        rows = table.find_all('tr')[1:]  # Skip header
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 4:
                doc_type = cells[3].text.strip()
                description = cells[1].text.strip()
                
                if doc_type == '10-K' or '10-K' in description:
                    link = cells[2].find('a')
                    if link:
                        href = link.get('href', '')
                        size_text = cells[4].text.strip() if len(cells) > 4 else '0'
                        
                        # 파일 크기 파싱
                        size = 0
                        if 'KB' in size_text:
                            size = float(size_text.replace('KB', '').strip())
                        elif 'MB' in size_text:
                            size = float(size_text.replace('MB', '').strip()) * 1024
                        
                        candidates.append({
                            'href': href,
                            'description': description,
                            'size': size,
                            'is_ixbrl': 'ix?' in href
                        })
        
        if not candidates:
            print("❌ No 10-K file found")
            return None
        
        # 일반 HTML 우선, 그 다음 크기 큰 것
        non_ixbrl = [c for c in candidates if not c['is_ixbrl']]
        
        if non_ixbrl:
            # 가장 큰 일반 HTML
            best = max(non_ixbrl, key=lambda x: x['size'])
        else:
            # iXBRL이라도 가장 큰 것
            best = max(candidates, key=lambda x: x['size'])
        
        full_url = self.BASE_URL + best['href']
        print(f"✅ 10-K File: {full_url}")
        print(f"   Size: {best['size']:.1f} KB")
        print(f"   iXBRL: {best['is_ixbrl']}")
        
        return full_url
    
    def download_full_10k(self, url):
        """전체 10-K HTML 다운로드"""
        print(f"\n📥 Downloading full 10-K...")
        
        response = requests.get(url, headers=self.headers)
        time.sleep(0.1)
        
        html = response.text
        
        print(f"✅ Downloaded: {len(html):,} characters ({len(html)/1024:.1f} KB)")
        
        return html
    
    def parse_full_10k(self, html):
        """전체 10-K 파싱"""
        
        print(f"\n🔍 Parsing 10-K structure...")
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 텍스트 추출
        full_text = soup.get_text(separator='\n', strip=False)
        
        # 불필요한 연속 공백 제거
        full_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', full_text)
        
        print(f"✅ Full text: {len(full_text):,} characters")
        
        # Part I
        part1 = self.extract_part_i(full_text)
        
        return {
            'full_text_length': len(full_text),
            'part_i': part1,
        }
    
    def extract_part_i(self, text):
        """Part I 추출"""
        
        print(f"\n📄 Extracting Part I...")
        
        sections = {}
        
        # Item 1: Business
        item1 = self.extract_section(
            text,
            start_patterns=[
                r'ITEM\s+1[\.\:]?\s+BUSINESS',
                r'Item\s+1[\.\:]?\s+Business',
            ],
            end_patterns=[
                r'ITEM\s+1A[\.\:]?\s+RISK\s+FACTORS',
                r'Item\s+1A[\.\:]?\s+Risk\s+Factors',
            ],
            section_name='Item 1: Business'
        )
        if item1:
            sections['item_1_business'] = item1
        
        # Item 1A: Risk Factors
        item1a = self.extract_section(
            text,
            start_patterns=[
                r'ITEM\s+1A[\.\:]?\s+RISK\s+FACTORS',
                r'Item\s+1A[\.\:]?\s+Risk\s+Factors',
            ],
            end_patterns=[
                r'ITEM\s+1B[\.\:]?\s+UNRESOLVED\s+STAFF\s+COMMENTS',
                r'Item\s+1B[\.\:]?\s+Unresolved\s+Staff\s+Comments',
                r'ITEM\s+2[\.\:]?\s+PROPERTIES',
                r'Item\s+2[\.\:]?\s+Properties',
            ],
            section_name='Item 1A: Risk Factors'
        )
        if item1a:
            sections['item_1a_risk_factors'] = item1a
        
        # Item 7: MD&A
        item7 = self.extract_section(
            text,
            start_patterns=[
                r'ITEM\s+7[\.\:]?\s+MANAGEMENT.*?DISCUSSION\s+AND\s+ANALYSIS',
                r'Item\s+7[\.\:]?\s+Management.*?Discussion\s+and\s+Analysis',
            ],
            end_patterns=[
                r'ITEM\s+7A[\.\:]?\s+QUANTITATIVE\s+AND\s+QUALITATIVE',
                r'Item\s+7A[\.\:]?\s+Quantitative\s+and\s+Qualitative',
                r'ITEM\s+8[\.\:]?\s+FINANCIAL\s+STATEMENTS',
                r'Item\s+8[\.\:]?\s+Financial\s+Statements',
            ],
            section_name='Item 7: MD&A'
        )
        if item7:
            sections['item_7_mda'] = item7
        
        return sections
    
    def extract_section(self, text, start_patterns, end_patterns, section_name):
        """섹션 추출 (시작/끝 패턴 매칭)"""
        
        # 시작 위치 찾기
        start_pos = None
        for pattern in start_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                start_pos = match.start()
                print(f"   ✅ Found {section_name} at position {start_pos:,}")
                break
        
        if not start_pos:
            print(f"   ⚠️ {section_name} not found")
            return None
        
        # 끝 위치 찾기
        end_pos = None
        search_start = start_pos + 500  # 시작 후 500자 뒤부터 검색
        
        for pattern in end_patterns:
            match = re.search(pattern, text[search_start:], re.IGNORECASE | re.DOTALL)
            if match:
                end_pos = search_start + match.start()
                print(f"   ✅ End at position {end_pos:,}")
                break
        
        if not end_pos:
            # 끝을 못 찾으면 100KB만
            end_pos = min(start_pos + 100000, len(text))
            print(f"   ⚠️ End not found, using {end_pos:,}")
        
        section_text = text[start_pos:end_pos]
        
        # 통계
        char_count = len(section_text)
        word_count = len(section_text.split())
        line_count = len(section_text.split('\n'))
        
        print(f"   📊 Extracted: {char_count:,} chars, {word_count:,} words, {line_count:,} lines")
        
        return {
            'text': section_text,
            'char_count': char_count,
            'word_count': word_count,
            'line_count': line_count,
        }
    
    def analyze_section_content(self, section_text):
        """섹션 내용 분석 (키워드, 패턴 추출)"""
        
        # 이건 Claude(나)가 직접 분석!
        # - 제품명 추출
        # - 숫자 데이터 추출
        # - 경쟁사 언급
        # - 리스크 카테고리
        # 등
        
        pass
    
    def save_full_10k(self, ticker, data):
        """전체 10-K 저장"""
        
        output_file = f'data/full_10k_{ticker}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved to {output_file}")
        
        # 통계 출력
        print(f"\n{'='*70}")
        print(f"📊 10-K Statistics for {ticker}")
        print(f"{'='*70}")
        
        part1 = data.get('parsed', {}).get('part_i', {})
        
        for section_key, section_name in [
            ('item_1_business', 'Item 1: Business'),
            ('item_1a_risk_factors', 'Item 1A: Risk Factors'),
            ('item_7_mda', 'Item 7: MD&A'),
        ]:
            section = part1.get(section_key)
            if section:
                print(f"\n{section_name}:")
                print(f"  Characters: {section['char_count']:,}")
                print(f"  Words: {section['word_count']:,}")
                print(f"  Lines: {section['line_count']:,}")
        
        print(f"{'='*70}")


# 실행
if __name__ == "__main__":
    print("="*70)
    print("🚀 완전한 10-K 사업보고서 수집")
    print("="*70)
    print()
    print("💡 목표: 전체 10-K를 완전히 파싱하여 구조화된 데이터로 변환")
    print("💡 차별화: 다른 서비스는 안 하는 완전한 데이터화!")
    print()
    
    collector = Full10KCollector()
    
    # AAPL 테스트
    ticker = "AAPL"
    
    print(f"📊 Collecting {ticker} 10-K...")
    print("="*70)
    
    # 1. Filing 정보
    filing_info = collector.get_latest_10k_filing(ticker)
    
    if not filing_info:
        print("❌ Failed to get filing info")
        exit(1)
    
    # 2. HTML 파일 찾기
    htm_url = collector.find_10k_htm_file(filing_info['documents_url'])
    
    if not htm_url:
        print("❌ Failed to find 10-K HTML file")
        exit(1)
    
    # 3. 다운로드
    html = collector.download_full_10k(htm_url)
    
    # 4. 파싱
    parsed = collector.parse_full_10k(html)
    
    # 5. 저장
    result = {
        'ticker': ticker,
        'collected_at': datetime.now().isoformat(),
        'filing_info': filing_info,
        'source_url': htm_url,
        'parsed': parsed,
    }
    
    collector.save_full_10k(ticker, result)
    
    print(f"\n🎉 {ticker} 10-K 수집 완료!")

