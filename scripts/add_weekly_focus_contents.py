"""이번 주 브리핑용 샘플 큐레이션 6개 추가

주간 브리핑을 작성하면서 바로 활용할 수 있는 거시/AI/반도체/밸류에이션 콘텐츠를 미리 넣어둡니다.
URL은 실제 확인 후 교체하세요.
"""

import os
import sys
import django


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.content.models import ContentSource, ContentCategory, CuratedContent  # noqa: E402


def get_source(slug: str) -> ContentSource:
    return ContentSource.objects.get(slug=slug)


def get_category(slug: str) -> ContentCategory:
    return ContentCategory.objects.get(slug=slug)


def add_weekly_focus_contents():
    print('=' * 80)
    print('🗓️ 이번 주 브리핑 샘플 큐레이션 추가')
    print('=' * 80)

    sources = {
        'sampro': get_source('sampro-tv'),
        'sinsaimdang': get_source('sinsaimdang'),
        'orangeboard': get_source('orangeboard'),
        'fint': get_source('fint'),
        'bookon': get_source('book-on-tv'),
        'shuka': get_source('shuka-world'),
    }

    categories = {
        'macro': get_category('macro-economy'),
        'industry': get_category('industry'),
        'financials': get_category('financial-statement'),
        'philosophy': get_category('philosophy'),
    }

    contents_data = [
        {
            'title': '금리 사이클과 2025년 증시 시나리오',
            'description': '연준 점도표, 실질 금리, 유동성 흐름을 종합적으로 설명해 금리와 증시의 상관관계를 복기합니다.',
            'source': sources['sampro'],
            'url': 'https://www.youtube.com/watch?v=TODO_RATE2025',
            'thumbnail': '',
            'creator': '삼프로TV',
            'duration': '52분',
            'category': categories['macro'],
            'difficulty': 3,
            'tags': ['거시경제', '금리', '연준'],
            'priority': 120,
            'is_featured': True,
            'curator_note': (
                '이번 주 주간 브리핑의 시장 리뷰 섹션에 바로 인용 가능한 핵심 자료입니다. '
                '연준 점도표와 실질 금리 흐름이 정리되어 있어 금리-성장주 밸류에이션 연동을 설명하기 좋습니다.'
            ),
        },
        {
            'title': 'AI 인프라 CAPEX 지도: 2025년 빅테크 투자 계획',
            'description': 'MSFT, GOOG, META의 데이터센터 투자 로드맵과 GPU 수요 전망을 정리해주는 최신 컨퍼런스 리뷰입니다.',
            'source': sources['fint'],
            'url': 'https://www.youtube.com/watch?v=TODO_AICAPEX',
            'thumbnail': '',
            'creator': '핀트',
            'duration': '36분',
            'category': categories['industry'],
            'difficulty': 4,
            'tags': ['AI', '클라우드', 'CAPEX'],
            'priority': 110,
            'is_featured': True,
            'curator_note': (
                '주간 브리핑 2️⃣ 테크·AI·반도체 인사이트 섹션에서 사용할 핵심 레퍼런스. '
                'MSFT/GOOG의 2025 CAPEX 가이던스가 표로 정리되어 있어, GPU 수요 지속 여부를 설명하기 적합합니다.'
            ),
        },
        {
            'title': 'TSMC vs Samsung 파운드리: 3나노 경쟁 현황',
            'description': '3나노 공정 수율, 고객사 확보 현황, 장비 업체의 체감 데이터를 비교해 반도체 업황을 진단합니다.',
            'source': sources['orangeboard'],
            'url': 'https://www.youtube.com/watch?v=TODO_FOUNDRY',
            'thumbnail': '',
            'creator': '오렌지보드',
            'duration': '41분',
            'category': categories['industry'],
            'difficulty': 4,
            'tags': ['반도체', '파운드리', 'TSMC', 'Samsung'],
            'priority': 105,
            'is_featured': True,
            'curator_note': (
                '반도체 섹션에서 “TSMC 수율 개선 vs 삼성의 고객 확보”라는 논점을 정리할 때 참고하세요. '
                '장비 업체 인터뷰와 웨이퍼 투입량 데이터가 함께 포함되어 있어 숫자를 곁들인 설명이 가능합니다.'
            ),
        },
        {
            'title': '엔비디아 실적 리포트로 배우는 손익계산서 체크포인트',
            'description': 'AI 칩 기업의 손익계산서를 사례로 매출/매출총이익/영업이익률을 빠르게 점검하는 방법을 알려줍니다.',
            'source': sources['sinsaimdang'],
            'url': 'https://www.youtube.com/watch?v=TODO_NVDA_PL',
            'thumbnail': '',
            'creator': '신사임당',
            'duration': '28분',
            'category': categories['financials'],
            'difficulty': 2,
            'tags': ['재무제표', 'NVDA', '손익계산서'],
            'priority': 102,
            'is_required': True,
            'curator_note': (
                '주간 브리핑 4️⃣ 신규 아이디어 & 밸류 스냅샷을 작성할 때 참고용으로 넣어두는 교육 콘텐츠입니다. '
                '손익계산서 주요 라인을 빠르게 복기할 수 있어, 엔비디아뿐 아니라 다른 종목에도 응용 가능합니다.'
            ),
        },
        {
            'title': '워렌 버핏의 “현금흐름” 해석법',
            'description': '버핏이 주주 서한에서 반복적으로 강조한 FCF와 자사주 매입의 의미를 해설합니다.',
            'source': sources['bookon'],
            'url': 'https://www.youtube.com/watch?v=TODO_BUFFETT_FCF',
            'thumbnail': '',
            'creator': '부크온TV',
            'duration': '22분',
            'category': categories['philosophy'],
            'difficulty': 2,
            'tags': ['워렌버핏', 'FCF', '자사주매입'],
            'priority': 98,
            'curator_note': (
                '브리핑 마지막 “다음 주 액션”을 세울 때 마인드셋을 다잡아주는 콘텐츠. '
                '현금흐름 중심 사고방식을 한 번 더 상기시키고, 밸류에이션 계산의 기준을 정비하게 해줍니다.'
            ),
        },
        {
            'title': 'AI 버블인가? 실제 수요 vs 과열 논쟁 정리',
            'description': 'AI 투자 열풍을 버블과 실수요 관점에서 비교하고, 엔지니어 인터뷰를 곁들여 현장을 전합니다.',
            'source': sources['shuka'],
            'url': 'https://www.youtube.com/watch?v=TODO_AI_BUBBLE',
            'thumbnail': '',
            'creator': '슈카월드',
            'duration': '30분',
            'category': categories['macro'],
            'difficulty': 3,
            'tags': ['AI', '버블', '수요'],
            'priority': 96,
            'curator_note': (
                '주간 브리핑 시장 리뷰/산업 인사이트 섹션을 연결해주는 콘텐츠. '
                '과열에 대한 외부 시각과 현업 엔지니어의 체감 사이에서 균형 잡힌 논리를 정리할 때 도움이 됩니다.'
            ),
        },
    ]

    created = 0
    for data in contents_data:
        content, is_created = CuratedContent.objects.update_or_create(
            title=data['title'], defaults=data
        )
        if is_created:
            created += 1
            status = '✅ 생성'
        else:
            status = '🔄 업데이트'
        print(f"{status}: {content.title}")

    print('-' * 80)
    print(f'완료! 생성 {created}건 / 업데이트 {len(contents_data) - created}건')
    print('URL의 TODO 부분은 실제 영상/아티클 링크로 교체하세요.')
    print('=' * 80)


if __name__ == '__main__':
    add_weekly_focus_contents()



