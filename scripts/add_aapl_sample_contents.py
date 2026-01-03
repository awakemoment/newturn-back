"""
AAPL 샘플 큐레이션 10개

실제 영상을 찾아서 URL을 교체하세요.
내용 분석과 큐레이터 노트는 이미 작성되어 있습니다.
"""
import os
import sys
import django

# Django 설정
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.content.models import ContentSource, ContentCategory, CuratedContent
from apps.stocks.models import Stock


def add_aapl_contents():
    print("=" * 80)
    print("📱 AAPL 샘플 큐레이션 추가")
    print("=" * 80)
    
    # AAPL 종목 가져오기
    try:
        aapl = Stock.objects.get(stock_code='AAPL')
        print(f"\n✅ 종목: {aapl.stock_name} ({aapl.stock_code})")
    except Stock.DoesNotExist:
        print("\n❌ AAPL 종목을 찾을 수 없습니다!")
        return
    
    # 소스 & 카테고리 가져오기
    sources = {
        '슈카월드': ContentSource.objects.get(slug='shuka-world'),
        '신사임당': ContentSource.objects.get(slug='sinsaimdang'),
        '오렌지보드': ContentSource.objects.get(slug='orangeboard'),
        '삼프로TV': ContentSource.objects.get(slug='sampro-tv'),
        '부크온TV': ContentSource.objects.get(slug='book-on-tv'),
        '존리': ContentSource.objects.get(slug='john-lee'),
        '월급쟁이부자들': ContentSource.objects.get(slug='wgb'),
        '인프런': ContentSource.objects.get(slug='inflearn'),
    }
    
    categories = {
        '종목분석': ContentCategory.objects.get(slug='stock-analysis'),
        '초보자': ContentCategory.objects.get(slug='beginner'),
        '거시경제': ContentCategory.objects.get(slug='macro-economy'),
        '미국주식': ContentCategory.objects.get(slug='us-stocks'),
        '재무제표': ContentCategory.objects.get(slug='financial-statement'),
        '투자철학': ContentCategory.objects.get(slug='philosophy'),
        '산업분석': ContentCategory.objects.get(slug='industry'),
    }
    
    # AAPL 큐레이션 데이터
    contents_data = [
        # 1. 초보자 필수 (비즈니스 모델)
        {
            'title': '애플이 돈을 버는 법 - 비즈니스 모델 완전 정복',
            'description': '아이폰, 맥북, 애플워치부터 앱스토어, iCloud까지. 애플의 전체 수익 구조를 쉽게 설명합니다.',
            'source': sources['슈카월드'],
            'creator': '슈카',
            'url': 'https://www.youtube.com/watch?v=SAMPLE_ID_1',  # 실제 URL로 교체
            'thumbnail': 'https://i.ytimg.com/vi/SAMPLE_ID_1/maxresdefault.jpg',
            'duration': '32분',
            'difficulty': 1,
            'category': categories['초보자'],
            'tags': ['AAPL', '비즈니스모델', '초보자', '빅테크'],
            'is_required': True,
            'priority': 100,
            'curator_note': """
AAPL 투자 전 반드시 봐야 할 영상입니다.

**왜 추천하나요?**
- 애플의 수익 구조를 처음부터 끝까지 설명
- 아이폰(60%), 서비스(20%), 기타(20%) 비중 이해
- 생태계 전략의 위력 (Lock-in Effect)

**이걸 보면:**
- 왜 애플이 마진율이 높은지
- 왜 서비스 매출이 중요한지
- 왜 애플 주가가 비싼지 이해 가능

**투자 판단:**
단순 하드웨어 회사가 아님 → 높은 밸류에이션 정당화
            """.strip(),
        },
        
        # 2. 재무제표 이해
        {
            'title': '빅테크 재무제표 읽는 법 - 애플편',
            'description': '애플의 10-K 리포트를 함께 읽으며 재무제표 핵심 지표를 배웁니다. FCF, ROE, 부채비율 등',
            'source': sources['신사임당'],
            'creator': '신사임당',
            'url': 'https://www.youtube.com/watch?v=SAMPLE_ID_2',
            'thumbnail': 'https://i.ytimg.com/vi/SAMPLE_ID_2/maxresdefault.jpg',
            'duration': '45분',
            'difficulty': 2,
            'category': categories['재무제표'],
            'tags': ['AAPL', '재무제표', 'FCF', 'ROE'],
            'is_required': True,
            'priority': 95,
            'curator_note': """
재무제표를 실전에서 어떻게 읽는지 배웁니다.

**핵심 내용:**
- FCF $100B/년의 의미
- ROE 147%의 놀라운 수익성
- 부채 $120B vs 현금 $160B (건전)

**이걸 보면:**
- Newturn의 메이트 점수 이해
- 밸류에이션 로직 이해
- 다른 종목도 직접 분석 가능

**추천 시점:**
Newturn에서 재무 데이터 볼 때 같이 보기
            """.strip(),
        },
        
        # 3. 실적 분석 (전문가)
        {
            'title': 'AAPL 2024 Q3 실적 완전 분석 - 아이폰 판매 부진 우려',
            'description': '애플의 최신 분기 실적을 심층 분석. 제품별 매출, 지역별 성장률, 가이던스까지',
            'source': sources['오렌지보드'],
            'creator': '오렌지보드',
            'url': 'https://www.youtube.com/watch?v=SAMPLE_ID_3',
            'thumbnail': 'https://i.ytimg.com/vi/SAMPLE_ID_3/maxresdefault.jpg',
            'duration': '1시간 5분',
            'difficulty': 4,
            'category': categories['종목분석'],
            'tags': ['AAPL', '실적분석', '아이폰', '서비스매출'],
            'is_featured': True,
            'priority': 90,
            'curator_note': """
최신 실적을 전문가 관점에서 분석합니다.

**핵심 포인트:**
- 아이폰 판매 -3% (우려)
- 서비스 매출 +15% (긍정)
- 중국 매출 -8% (리스크)
- Vision Pro 기대감

**투자 시사점:**
단기 조정은 매수 기회. 서비스 성장세가 밸류에이션 지지

**보는 타이밍:**
실적 발표 직후, 투자 판단 전
            """.strip(),
        },
        
        # 4. 거시경제 맥락
        {
            'title': '금리 인상이 기술주에 미치는 영향 - AAPL은?',
            'description': '고금리 환경에서 성장주 밸류에이션 부담. 하지만 애플은 다르다?',
            'source': sources['삼프로TV'],
            'creator': '삼프로',
            'url': 'https://www.youtube.com/watch?v=SAMPLE_ID_4',
            'thumbnail': 'https://i.ytimg.com/vi/SAMPLE_ID_4/maxresdefault.jpg',
            'duration': '38분',
            'difficulty': 3,
            'category': categories['거시경제'],
            'tags': ['금리', '기술주', 'AAPL', '밸류에이션'],
            'priority': 85,
            'curator_note': """
거시경제가 AAPL에 미치는 영향을 이해합니다.

**핵심 개념:**
- 금리 ↑ → 할인율 ↑ → 밸류에이션 ↓
- 하지만 AAPL은 현금 $160B 보유
- 고금리로 이자 수익 증가

**투자 전략:**
금리 하락 기대 시 → 적극 매수
금리 상승 시 → 보수적 접근

**Newturn 활용:**
그로우(DCF) 점수와 함께 보기
            """.strip(),
        },
        
        # 5. 경쟁 환경
        {
            'title': '애플 vs 삼성 vs 구글 - 빅테크 3파전',
            'description': '프리미엄 스마트폰 시장의 경쟁 구도. 애플의 압도적 우위와 위협 요소',
            'source': sources['신사임당'],
            'creator': '신사임당',
            'url': 'https://www.youtube.com/watch?v=SAMPLE_ID_5',
            'thumbnail': 'https://i.ytimg.com/vi/SAMPLE_ID_5/maxresdefault.jpg',
            'duration': '28분',
            'difficulty': 2,
            'category': categories['산업분석'],
            'tags': ['AAPL', '경쟁분석', '삼성', '구글'],
            'priority': 80,
            'curator_note': """
애플의 경쟁력을 객관적으로 평가합니다.

**경쟁 우위:**
- 브랜드 파워 (프리미엄 시장 70% 점유)
- 생태계 (한번 들어오면 못 나감)
- 마진율 38% (삼성 15%)

**위협 요소:**
- 중국 화웨이 반등
- 규제 압박 (앱스토어 수수료)

**투자 판단:**
Moat(해자)가 깊음 → 장기 보유 적합
            """.strip(),
        },
        
        # 6. 투자 철학
        {
            'title': '워렌 버핏은 왜 애플에 투자했나?',
            'description': '가치투자의 전설이 기술주에 투자한 이유. 버핏의 AAPL 투자 철학',
            'source': sources['부크온TV'],
            'creator': '부크온',
            'url': 'https://www.youtube.com/watch?v=SAMPLE_ID_6',
            'thumbnail': 'https://i.ytimg.com/vi/SAMPLE_ID_6/maxresdefault.jpg',
            'duration': '25분',
            'difficulty': 2,
            'category': categories['투자철학'],
            'tags': ['AAPL', '워렌버핏', '가치투자', '장기투자'],
            'is_featured': True,
            'priority': 88,
            'curator_note': """
버핏의 AAPL 투자를 통해 가치투자를 배웁니다.

**버핏의 논리:**
- 기술주가 아닌 "소비재 회사"
- 브랜드 파워 = 해자(Moat)
- 막대한 현금흐름
- 주주 환원 정책 (자사주 매입)

**Newturn 연결:**
베니(그레이엄) 관점과 일치
→ 안전마진 + 우량 자산

**투자 교훈:**
단기 변동성 무시, 장기 보유
            """.strip(),
        },
        
        # 7. 장기 투자
        {
            'title': '애플 10년 보유하면 얼마? - 복리의 마법',
            'description': '2014년 $100 → 2024년 $500. 배당 재투자까지 포함한 실제 수익률',
            'source': sources['존리'],
            'creator': '존리',
            'url': 'https://www.youtube.com/watch?v=SAMPLE_ID_7',
            'thumbnail': 'https://i.ytimg.com/vi/SAMPLE_ID_7/maxresdefault.jpg',
            'duration': '20분',
            'difficulty': 1,
            'category': categories['투자철학'],
            'tags': ['AAPL', '장기투자', '복리', '존리'],
            'priority': 75,
            'curator_note': """
장기 투자의 위력을 실제 사례로 보여줍니다.

**놀라운 수치:**
- 10년 수익률: +400%
- 배당 재투자: +50%p 추가
- 연평균: 17.5% (S&P500의 2배)

**존리의 조언:**
- 타이밍보다 타임(Time)
- 좋은 회사를 싸게 사서 오래 보유
- 복리는 시간의 함수

**Newturn 활용:**
적정가 이하에서 사서 10년 보유 전략
            """.strip(),
        },
        
        # 8. 체계적 강의
        {
            'title': '[월부] 미국 주식 완전 정복 - 애플 사례 연구',
            'description': '미국 주식 투자의 모든 것. 애플을 예시로 세금, 환율, 배당까지',
            'source': sources['월급쟁이부자들'],
            'creator': '월급쟁이부자들',
            'url': 'https://wealthmasters.kr/courses/apple-case-study',
            'duration': '2시간 30분',
            'difficulty': 2,
            'category': categories['미국주식'],
            'tags': ['AAPL', '미국주식', '세금', '환율'],
            'priority': 70,
            'curator_note': """
미국 주식 투자의 실전 지식을 체계적으로 배웁니다.

**강의 내용:**
1. 계좌 개설 (해외 주식)
2. 매수/매도 방법
3. 배당금 세금 (15%)
4. 환율 리스크 관리
5. 연말 세금 보고

**실용성:**
이론이 아닌 실전 경험 기반
AAPL 실제 매수부터 세금까지

**추천 대상:**
미국 주식 처음 시작하는 분
            """.strip(),
        },
        
        # 9. 데이터 분석
        {
            'title': '파이썬으로 애플 주식 분석하기 - 퀀트 입문',
            'description': 'Python과 Pandas로 AAPL의 재무 데이터를 분석. 실전 코드 포함',
            'source': sources['인프런'],
            'creator': '데이터 분석가',
            'url': 'https://www.inflearn.com/course/apple-stock-analysis',
            'duration': '3시간',
            'difficulty': 4,
            'category': categories['종목분석'],
            'tags': ['AAPL', 'Python', '데이터분석', '퀀트'],
            'priority': 60,
            'curator_note': """
프로그래밍으로 투자 분석하는 방법을 배웁니다.

**배우는 내용:**
- EDGAR에서 재무 데이터 가져오기
- FCF, ROE 계산
- DCF 밸류에이션 구현
- 백테스팅

**Newturn 연결:**
Newturn이 내부적으로 하는 일을 이해
→ 더 신뢰하고 활용 가능

**추천 대상:**
개발자, 데이터 분석가
퀀트 투자에 관심 있는 분
            """.strip(),
        },
        
        # 10. 최신 이슈
        {
            'title': 'Vision Pro 출시, 애플의 미래는? - AR/VR 시장 전망',
            'description': '애플의 새로운 성장 동력 Vision Pro. 시장 반응과 투자 관점 분석',
            'source': sources['오렌지보드'],
            'creator': '오렌지보드',
            'url': 'https://www.youtube.com/watch?v=SAMPLE_ID_10',
            'thumbnail': 'https://i.ytimg.com/vi/SAMPLE_ID_10/maxresdefault.jpg',
            'duration': '35분',
            'difficulty': 3,
            'category': categories['산업분석'],
            'tags': ['AAPL', 'VisionPro', 'AR', 'VR', '신제품'],
            'is_featured': True,
            'priority': 92,
            'curator_note': """
애플의 차세대 성장 동력을 평가합니다.

**긍정적 요소:**
- 새로운 카테고리 창출
- 프리미엄 포지셔닝
- 개발자 생태계

**우려 요소:**
- 높은 가격 ($3,499)
- 제한된 초기 시장
- 2-3년 후 대중화

**투자 판단:**
단기: 중립 (실적 기여 미미)
장기: 긍정 (3-5년 후 성장 동력)

**그로우(Fisher) 관점:**
미래 성장 잠재력 → 높은 점수
            """.strip(),
        },
    ]
    
    # 데이터 입력
    created_count = 0
    
    for idx, data in enumerate(contents_data, 1):
        content, created = CuratedContent.objects.get_or_create(
            title=data['title'],
            defaults=data
        )
        
        if created:
            # AAPL에 추천
            content.recommended_for_stocks.add(aapl)
            print(f"\n{idx}. ✅ {content.title}")
            print(f"   소스: {content.source.name}")
            print(f"   난이도: {'⭐' * content.difficulty}")
            print(f"   카테고리: {content.category.name}")
            created_count += 1
        else:
            print(f"\n{idx}. ⚠️ 이미 존재: {content.title}")
    
    print("\n" + "=" * 80)
    print(f"✅ 완료! {created_count}개 콘텐츠 추가")
    print("=" * 80)
    
    # Admin URL 출력
    print(f"\n📍 Admin에서 확인:")
    print(f"   http://localhost:8000/admin/content/curatedcontent/")
    print(f"\n📍 AAPL 추천 콘텐츠:")
    aapl_contents = CuratedContent.objects.filter(recommended_for_stocks=aapl).order_by('-priority')
    print(f"   총 {aapl_contents.count()}개")
    
    print("\n💡 다음 단계:")
    print("   1. Admin에서 실제 YouTube URL로 교체")
    print("   2. thumbnail URL 업데이트")
    print("   3. Learn 탭 UI 구현")
    print("=" * 80)


if __name__ == '__main__':
    add_aapl_contents()

