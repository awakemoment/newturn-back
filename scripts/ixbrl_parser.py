"""
iXBRL 10-K 파서
SEC의 최신 표준 형식인 iXBRL(Inline XBRL)을 완전히 파싱

목표:
1. 전체 10-K HTML 추출
2. 재무 데이터 태그 파싱
3. Item별 섹션 구조화
4. 테이블 데이터 추출
5. 제품/지역/경쟁사 정보 추출

이것이 뉴턴의 핵심 자산!
"""
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import time


class iXBRLParser:
    """iXBRL 10-K 완전 파서"""
    
    BASE_URL = "https://www.sec.gov"
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Newturn AI Investment Platform contact@newturn.ai',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
    
    def get_cik(self, ticker):
        """티커 → CIK"""
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, headers=self.headers)
        time.sleep(0.11)  # SEC rate limit: 10 requests/second
        
        data = response.json()
        for key, company in data.items():
            if company['ticker'].upper() == ticker.upper():
                return str(company['cik_str']).zfill(10)
        return None
    
    def get_latest_10k(self, ticker):
        """최신 10-K 메타데이터"""
        cik = self.get_cik(ticker)
        if not cik:
            return None
        
        print(f"✅ {ticker} CIK: {cik}")
        
        # EDGAR Search (기존 방식)
        # 10-K와 10-K/A 모두 검색
        url = f"{self.BASE_URL}/cgi-bin/browse-edgar"
        params = {
            'action': 'getcompany',
            'CIK': cik,
            'type': '10-K',  # 10-K와 10-K/A 모두 포함
            'dateb': '',  # 최신
            'owner': 'exclude',
            'count': '3',  # 최근 3개 확인 (10-K/A 고려)
        }
        
        response = requests.get(url, params=params, headers=self.headers)
        time.sleep(0.11)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Filing info from table
        table = soup.find('table', class_='tableFile2')
        if not table:
            return None
        
        rows = table.find_all('tr')[1:]  # Skip header
        if not rows:
            return None
        
        # 10-K 또는 10-K/A 찾기 (10-K/A 우선)
        target_row = None
        for row in rows[:3]:
            cells = row.find_all('td')
            filing_type = cells[0].text.strip()
            if filing_type in ['10-K', '10-K/A']:
                target_row = row
                print(f"✅ Found: {filing_type}")
                break
        
        if not target_row:
            return None
        
        cells = target_row.find_all('td')
        filing_date = cells[3].text.strip()
        
        # Documents button
        doc_button = target_row.find('a', {'id': 'documentsbutton'})
        if not doc_button:
            return None
        
        documents_url = self.BASE_URL + doc_button['href']
        
        print(f"✅ 10-K Found: {filing_date}")
        print(f"   Documents: {documents_url}")
        
        # Get actual HTML file
        response2 = requests.get(documents_url, headers=self.headers)
        time.sleep(0.11)
        
        soup2 = BeautifulSoup(response2.content, 'html.parser')
        table2 = soup2.find('table', class_='tableFile')
        
        if not table2:
            return None
        
        # Find 10-K document (10-K 또는 10-K/A)
        # ix? 링크가 아닌 실제 .htm 파일 찾기
        for row in table2.find_all('tr')[1:]:
            cells = row.find_all('td')
            if len(cells) >= 4:
                doc_type = cells[3].text.strip()
                description = cells[1].text.strip()
                
                # 10-K 또는 10-K/A 모두 허용
                if doc_type in ['10-K', '10-K/A'] or '10-K' in description:
                    link = cells[2].find('a')
                    if link:
                        href = link.get('href', '')
                        primary_doc = link.text.strip()
                        
                        # ix? 링크 건너뛰기, 실제 .htm 파일만
                        if 'ix?' not in href and primary_doc.endswith('.htm'):
                            doc_url = self.BASE_URL + href
                            
                            print(f"   Document: {primary_doc}")
                            print(f"   Type: {doc_type}")
                            print(f"   URL: {doc_url}")
                            
                            return {
                                'ticker': ticker,
                                'cik': cik,
                                'filing_date': filing_date,
                                'document_url': doc_url,
                                'primary_document': primary_doc,
                                'filing_type': doc_type,
                            }
        
        # 실제 .htm 못 찾으면 아무거나 (10-K/A 포함)
        print("   ⚠️ No direct .htm found, trying any 10-K or 10-K/A...")
        for row in table2.find_all('tr')[1:]:
            cells = row.find_all('td')
            if len(cells) >= 4:
                doc_type = cells[3].text.strip()
                description = cells[1].text.strip()
                
                # 10-K 또는 10-K/A
                if doc_type in ['10-K', '10-K/A'] or '10-K' in description:
                    link = cells[2].find('a')
                    if link:
                        href = link.get('href', '')
                        # ix? 링크면 실제 파일 경로로 변환
                        if 'ix?doc=' in href:
                            # ix?doc=/Archives/... → 직접 경로
                            actual_path = href.split('ix?doc=')[1]
                            doc_url = self.BASE_URL + actual_path
                        else:
                            doc_url = self.BASE_URL + href
                        
                        primary_doc = link.text.strip()
                        
                        print(f"   Document (converted): {primary_doc}")
                        print(f"   Type: {doc_type}")
                        print(f"   URL: {doc_url}")
                        
                        return {
                            'ticker': ticker,
                            'cik': cik,
                            'filing_date': filing_date,
                            'document_url': doc_url,
                            'primary_document': primary_doc,
                            'filing_type': doc_type,
                        }
        
        return None
    
    def download_10k_html(self, doc_url):
        """10-K HTML 다운로드"""
        print(f"\n📥 Downloading: {doc_url}")
        
        response = requests.get(doc_url, headers=self.headers)
        time.sleep(0.11)
        
        html = response.text
        
        print(f"✅ Downloaded: {len(html):,} bytes ({len(html)/1024:.1f} KB)")
        
        return html
    
    def parse_ixbrl_10k(self, html):
        """iXBRL 10-K 완전 파싱"""
        
        print(f"\n🔍 Parsing iXBRL 10-K...")
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 1. iXBRL 태그 제거하고 순수 텍스트만
        # ix:header, ix:hidden, ix:nonfraction 등 제거
        for tag in soup.find_all(['ix:header', 'ix:hidden']):
            tag.decompose()
        
        # 2. 본문 텍스트 추출
        # <body> 안의 모든 텍스트
        body = soup.find('body')
        
        if not body:
            print("⚠️ No <body> tag found, using whole document")
            text = soup.get_text(separator='\n', strip=False)
        else:
            text = body.get_text(separator='\n', strip=False)
        
        # 3. 정제
        # 연속 공백 제거
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        # 탭 제거
        text = re.sub(r'\t+', ' ', text)
        # 줄 끝 공백 제거
        lines = [line.rstrip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        print(f"✅ Extracted text: {len(text):,} characters")
        print(f"   Lines: {len(lines):,}")
        
        # 4. 구조 분석
        structure = self.analyze_document_structure(text)
        
        # 5. Item별 섹션 추출
        sections = self.extract_all_sections(text)
        
        return {
            'text_length': len(text),
            'line_count': len(lines),
            'structure': structure,
            'sections': sections,
        }
    
    def analyze_document_structure(self, text):
        """문서 구조 분석 (목차 찾기)"""
        
        print(f"\n📑 Analyzing document structure...")
        
        # TABLE OF CONTENTS 찾기
        toc_patterns = [
            r'TABLE\s+OF\s+CONTENTS',
            r'Index\s+to\s+Financial\s+Statements',
        ]
        
        toc_pos = None
        for pattern in toc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                toc_pos = match.start()
                print(f"✅ Found TOC at position {toc_pos:,}")
                break
        
        # Item 목록 찾기
        item_pattern = r'(?:PART|Part)\s+([IVX]+).*?(?:ITEM|Item)\s+(\d+[A-Z]?)'
        
        items = []
        for match in re.finditer(item_pattern, text[:50000] if toc_pos else text):  # 처음 50KB만
            part = match.group(1)
            item = match.group(2)
            items.append(f"Part {part} - Item {item}")
        
        if items:
            print(f"✅ Found {len(items)} items in document")
            for item in items[:10]:  # 처음 10개만 출력
                print(f"   - {item}")
        
        return {
            'has_toc': toc_pos is not None,
            'toc_position': toc_pos,
            'items_found': items,
        }
    
    def extract_all_sections(self, text):
        """모든 주요 섹션 추출"""
        
        print(f"\n📄 Extracting sections...")
        
        sections = {}
        
        # Item 1: Business
        item1 = self.extract_section_robust(
            text,
            section_name='Item 1: Business',
            start_patterns=[
                r'ITEM\s+1[\.\:\s]+BUSINESS',
                r'Item\s+1[\.\:\s]+Business',
                r'ITEM\s+1\s*\n+BUSINESS',
            ],
            end_patterns=[
                r'ITEM\s+1A[\.\:\s]+RISK',
                r'Item\s+1A[\.\:\s]+Risk',
            ]
        )
        if item1:
            sections['item_1_business'] = item1
        
        # Item 1A: Risk Factors
        item1a = self.extract_section_robust(
            text,
            section_name='Item 1A: Risk Factors',
            start_patterns=[
                r'ITEM\s+1A[\.\:\s]+RISK\s+FACTORS',
                r'Item\s+1A[\.\:\s]+Risk\s+Factors',
            ],
            end_patterns=[
                r'ITEM\s+1B[\.\:\s]+UNRESOLVED',
                r'Item\s+1B[\.\:\s]+Unresolved',
                r'ITEM\s+2[\.\:\s]+PROPERTIES',
                r'Item\s+2[\.\:\s]+Properties',
            ]
        )
        if item1a:
            sections['item_1a_risk_factors'] = item1a
        
        # Item 7: MD&A
        item7 = self.extract_section_robust(
            text,
            section_name='Item 7: MD&A',
            start_patterns=[
                r'ITEM\s+7[\.\:\s]+MANAGEMENT.*?DISCUSSION',
                r'Item\s+7[\.\:\s]+Management.*?Discussion',
                r'ITEM\s+7\s*\n+MANAGEMENT',
            ],
            end_patterns=[
                r'ITEM\s+7A[\.\:\s]+QUANTITATIVE',
                r'Item\s+7A[\.\:\s]+Quantitative',
                r'ITEM\s+8[\.\:\s]+FINANCIAL\s+STATEMENTS',
                r'Item\s+8[\.\:\s]+Financial\s+Statements',
            ]
        )
        if item7:
            sections['item_7_mda'] = item7
        
        return sections
    
    def extract_section_robust(self, text, section_name, start_patterns, end_patterns):
        """섹션 추출 (여러 패턴 시도)"""
        
        print(f"\n   🔍 Extracting {section_name}...")
        
        # 시작 위치 찾기
        start_pos = None
        matched_pattern = None
        
        for pattern in start_patterns:
            # DOTALL 플래그로 여러 줄 매칭
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                start_pos = match.start()
                matched_pattern = pattern
                print(f"      ✅ Found start at {start_pos:,} (pattern: {pattern[:50]}...)")
                break
        
        if not start_pos:
            print(f"      ⚠️ Start not found")
            return None
        
        # 끝 위치 찾기
        end_pos = None
        search_start = start_pos + 1000  # 시작 후 1000자 뒤부터
        
        for pattern in end_patterns:
            match = re.search(pattern, text[search_start:], re.IGNORECASE | re.DOTALL)
            if match:
                end_pos = search_start + match.start()
                print(f"      ✅ Found end at {end_pos:,}")
                break
        
        if not end_pos:
            # 끝을 못 찾으면 150KB 또는 텍스트 끝
            end_pos = min(start_pos + 150000, len(text))
            print(f"      ⚠️ End not found, using {end_pos:,}")
        
        # 추출
        section_text = text[start_pos:end_pos]
        
        # 통계
        char_count = len(section_text)
        word_count = len(section_text.split())
        line_count = len(section_text.split('\n'))
        
        # 페이지 추정 (1 page ≈ 3000 chars)
        page_estimate = char_count / 3000
        
        print(f"      📊 Extracted:")
        print(f"         Characters: {char_count:,}")
        print(f"         Words: {word_count:,}")
        print(f"         Lines: {line_count:,}")
        print(f"         Pages (est): {page_estimate:.1f}")
        
        return {
            'text': section_text,
            'char_count': char_count,
            'word_count': word_count,
            'line_count': line_count,
            'page_estimate': page_estimate,
            'start_position': start_pos,
            'end_position': end_pos,
        }
    
    def save_parsed_10k(self, ticker, metadata, parsed_data):
        """파싱 결과 저장"""
        
        output_file = f'data/parsed_10k_{ticker}.json'
        
        result = {
            'ticker': ticker,
            'collected_at': datetime.now().isoformat(),
            'filing_info': metadata,
            'parsed': parsed_data,
        }
        
        # 섹션 텍스트는 별도 파일로 (너무 큼)
        sections = parsed_data.get('sections', {})
        
        for section_key, section_data in sections.items():
            if section_data and 'text' in section_data:
                # 텍스트는 별도 파일
                text_file = f'data/section_{ticker}_{section_key}.txt'
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(section_data['text'])
                
                # JSON에는 파일 경로만
                section_data['text_file'] = text_file
                del section_data['text']
        
        # JSON 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved to {output_file}")
        
        return output_file


# 실행
if __name__ == "__main__":
    print("="*80)
    print("🚀 iXBRL 10-K 완전 파서")
    print("="*80)
    print()
    print("💡 목표: SEC의 최신 iXBRL 형식을 완전히 파싱")
    print("💡 차별화: 아무도 시도하지 않은 완전한 10-K 데이터화!")
    print("="*80)
    print()
    
    parser = iXBRLParser()
    
    # AAPL 테스트
    ticker = "AAPL"
    
    print(f"📊 Parsing {ticker} 10-K (Latest)...")
    print("="*80)
    
    # 1. 최신 10-K 메타데이터
    metadata = parser.get_latest_10k(ticker)
    
    if not metadata:
        print("❌ Failed to get 10-K metadata")
        exit(1)
    
    # 2. HTML 다운로드
    html = parser.download_10k_html(metadata['document_url'])
    
    # 3. 파싱
    parsed = parser.parse_ixbrl_10k(html)
    
    # 4. 저장
    output_file = parser.save_parsed_10k(ticker, metadata, parsed)
    
    # 5. 결과 요약
    print(f"\n{'='*80}")
    print(f"🎉 {ticker} 10-K 파싱 완료!")
    print(f"{'='*80}")
    
    print(f"\n📊 파싱 결과:")
    print(f"   Filing Date: {metadata['filing_date']}")
    print(f"   Total Text: {parsed['text_length']:,} characters")
    print(f"   Total Lines: {parsed['line_count']:,}")
    
    sections = parsed.get('sections', {})
    print(f"\n📄 추출된 섹션: {len(sections)}개")
    
    for section_name, section_data in sections.items():
        if section_data:
            print(f"\n   {section_name}:")
            print(f"      Words: {section_data['word_count']:,}")
            print(f"      Pages: ~{section_data['page_estimate']:.1f}")
    
    print(f"\n{'='*80}")
    print(f"✅ 저장 완료: {output_file}")
    print(f"{'='*80}")

