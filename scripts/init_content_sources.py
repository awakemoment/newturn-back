"""
콘텐츠 소스 초기 데이터 입력

우리가 조사한 모든 콘텐츠 소스를 DB에 입력합니다.
"""
import os
import sys
import django

# Django 설정
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.content.models import ContentSource, ContentCategory


def init_sources():
    print("=" * 80)
    print("📚 콘텐츠 소스 초기화")
    print("=" * 80)
    
    sources_data = [
        # ===== 유튜브 채널 =====
        {
            'name': '삼프로TV',
            'slug': 'sampro-tv',
            'source_type': 'youtube',
            'description': '경제 및 투자 관련 심층 분석을 제공하는 채널. 전문가 인터뷰와 FOMC 리뷰 등',
            'website': 'https://www.youtube.com/@sampro',
            'is_free': True,
            'price_info': '무료',
            'quality_rating': 5,
            'reliability': 5,
            'target_audience': '중급-고급',
            'specialty': '거시경제, 시장 분석',
            'order': 1,
        },
        {
            'name': '신사임당',
            'slug': 'sinsaimdang',
            'source_type': 'youtube',
            'description': '재테크, 부동산, 주식 등 실용적인 재무 지식 제공',
            'website': 'https://www.youtube.com/@sinsaimdang',
            'is_free': True,
            'price_info': '무료',
            'quality_rating': 4,
            'reliability': 4,
            'target_audience': '초급-중급',
            'specialty': '재테크 전반, 금리와 주가',
            'order': 2,
        },
        {
            'name': '슈카월드',
            'slug': 'shuka-world',
            'source_type': 'youtube',
            'description': '슈카의 빨간책방. 쉬운 설명과 엔터테인먼트',
            'website': 'https://www.youtube.com/@shukaworld',
            'is_free': True,
            'price_info': '무료',
            'quality_rating': 4,
            'reliability': 3,
            'target_audience': '초급',
            'specialty': '경제 상식, 부자들의 습관',
            'order': 3,
        },
        {
            'name': '김작가TV',
            'slug': 'kim-writer',
            'source_type': 'youtube',
            'description': '시사/경제 결합, 팟캐스트 스타일의 이슈픽',
            'website': 'https://www.youtube.com/@kimwriter',
            'is_free': True,
            'price_info': '무료',
            'quality_rating': 4,
            'reliability': 4,
            'target_audience': '중급',
            'specialty': '시사, 투자 인터뷰',
            'order': 4,
        },
        {
            'name': '한국주식방송',
            'slug': 'korea-stock-tv',
            'source_type': 'youtube',
            'description': '실시간 시황, 차트 분석, 장전 브리핑',
            'is_free': True,
            'price_info': '무료',
            'quality_rating': 3,
            'reliability': 3,
            'target_audience': '중급',
            'specialty': '종목 분석, 기술적 분석',
            'order': 5,
        },
        {
            'name': '부크온TV',
            'slug': 'book-on-tv',
            'source_type': 'youtube',
            'description': '책 리뷰와 투자 철학. 투자 고전 읽기',
            'is_free': True,
            'price_info': '무료',
            'quality_rating': 4,
            'reliability': 4,
            'target_audience': '중급-고급',
            'specialty': '투자 철학, 고전',
            'order': 6,
        },
        {
            'name': '존리의 부자되기',
            'slug': 'john-lee',
            'source_type': 'youtube',
            'description': '장기 투자 철학, 멘탈 관리, 존리의 한 마디',
            'is_free': True,
            'price_info': '무료',
            'quality_rating': 4,
            'reliability': 4,
            'target_audience': '초급-중급',
            'specialty': '장기 투자, 멘탈',
            'order': 7,
        },
        {
            'name': '오렌지보드',
            'slug': 'orangeboard',
            'source_type': 'youtube',
            'description': '미국 주식 심층 분석. 빅테크 실적 분석, 섹터 ETF',
            'is_free': True,
            'price_info': '무료',
            'quality_rating': 5,
            'reliability': 4,
            'target_audience': '중급',
            'specialty': '미국 주식, 빅테크',
            'order': 8,
        },
        {
            'name': '핀트',
            'slug': 'fint',
            'source_type': 'youtube',
            'description': '미국 경제 지표 해석. FOMC 완전 정복',
            'is_free': True,
            'price_info': '무료',
            'quality_rating': 5,
            'reliability': 5,
            'target_audience': '고급',
            'specialty': '미국 경제, FOMC',
            'order': 9,
        },
        
        # ===== 네이버 프리미엄 =====
        {
            'name': '돌핀투자비서',
            'slug': 'dolphin',
            'source_type': 'newsletter',
            'description': '종목 시그널, 매일 업데이트',
            'website': 'https://contents.premium.naver.com/dolphin',
            'is_free': False,
            'price_info': '월 9,900원',
            'quality_rating': 4,
            'reliability': 4,
            'target_audience': '중급',
            'specialty': '종목 시그널, 시장 브리핑',
            'order': 20,
        },
        {
            'name': 'ASSETX2',
            'slug': 'assetx2',
            'source_type': 'newsletter',
            'description': '자산배분의 정석. 자산배분 전략, ETF 투자',
            'website': 'https://contents.premium.naver.com/assetx2',
            'is_free': False,
            'price_info': '월 14,900원',
            'quality_rating': 5,
            'reliability': 5,
            'target_audience': '중급-고급',
            'specialty': '자산배분, ETF',
            'order': 21,
        },
        {
            'name': '주식단테',
            'slug': 'stock-dante',
            'source_type': 'newsletter',
            'description': '초보자 친화적 용어 설명, 경제 상식',
            'is_free': False,
            'price_info': '월 9,900원',
            'quality_rating': 3,
            'reliability': 3,
            'target_audience': '초급',
            'specialty': '경제 상식, 재무제표',
            'order': 22,
        },
        {
            'name': '스윙프로',
            'slug': 'swing-pro',
            'source_type': 'newsletter',
            'description': '차트 분석, 기술적 투자. 단기 매매 전략',
            'is_free': False,
            'price_info': '월 19,900원',
            'quality_rating': 4,
            'reliability': 3,
            'target_audience': '중급',
            'specialty': '차트 분석, 단기 매매',
            'order': 23,
        },
        
        # ===== 강의 플랫폼 =====
        {
            'name': '월급쟁이부자들',
            'slug': 'wgb',
            'source_type': 'platform',
            'description': '체계적 커리큘럼, 초보자 친화적 투자 교육',
            'website': 'https://www.wealthmasters.kr',
            'is_free': False,
            'price_info': '연회비 약 30만원',
            'quality_rating': 5,
            'reliability': 5,
            'target_audience': '초급-중급',
            'specialty': '체계적 투자 교육',
            'order': 30,
        },
        {
            'name': '인프런',
            'slug': 'inflearn',
            'source_type': 'platform',
            'description': 'IT 개발자 친화적, 데이터 분석 활용',
            'website': 'https://www.inflearn.com',
            'is_free': False,
            'price_info': '강의당 3-10만원',
            'quality_rating': 4,
            'reliability': 4,
            'target_audience': '중급',
            'specialty': '퀀트, 데이터 분석',
            'order': 31,
        },
        {
            'name': '클래스101',
            'slug': 'class101',
            'source_type': 'platform',
            'description': '친절한 설명, 예쁜 UI',
            'website': 'https://class101.net',
            'is_free': False,
            'price_info': '강의당 5-15만원',
            'quality_rating': 4,
            'reliability': 4,
            'target_audience': '초급',
            'specialty': '주식 기초, 미국 주식',
            'order': 32,
        },
        {
            'name': '탈잉',
            'slug': 'taling',
            'source_type': 'platform',
            'description': '1:1 또는 소그룹 과외. 맞춤형 학습',
            'website': 'https://taling.me',
            'is_free': False,
            'price_info': '시간당 3-10만원',
            'quality_rating': 4,
            'reliability': 4,
            'target_audience': '맞춤형',
            'specialty': '1:1 맞춤 학습',
            'order': 33,
        },
        
        # ===== 뉴스레터/블로그 =====
        {
            'name': '어피티',
            'slug': 'uppity',
            'source_type': 'newsletter',
            'description': 'MZ세대 재테크, 쉬운 설명',
            'website': 'https://uppity.co.kr',
            'is_free': True,
            'price_info': '무료 + 유료',
            'quality_rating': 4,
            'reliability': 4,
            'target_audience': 'MZ세대',
            'specialty': '재테크, 금융 상품',
            'order': 40,
        },
        {
            'name': 'EO (Economic Observer)',
            'slug': 'eo',
            'source_type': 'newsletter',
            'description': '해외 경제 뉴스 큐레이션',
            'is_free': True,
            'price_info': '무료',
            'quality_rating': 4,
            'reliability': 4,
            'target_audience': '중급',
            'specialty': '글로벌 경제',
            'order': 41,
        },
        
        # ===== 증권사 리포트 =====
        {
            'name': '증권사 리포트',
            'slug': 'securities-report',
            'source_type': 'report',
            'description': '삼성증권, NH투자증권, 한국투자증권 등 증권사 리서치 리포트',
            'is_free': True,
            'price_info': '무료 (증권사 앱 필요)',
            'quality_rating': 5,
            'reliability': 5,
            'target_audience': '중급-고급',
            'specialty': '산업 분석, 목표가',
            'order': 50,
        },
        
        # ===== 우리 콘텐츠 =====
        {
            'name': 'Newturn 주간 브리핑',
            'slug': 'newturn-weekly',
            'source_type': 'our_content',
            'description': 'Newturn팀이 직접 작성하는 주간 시장 브리핑',
            'is_free': True,
            'price_info': '무료',
            'quality_rating': 5,
            'reliability': 5,
            'target_audience': '전체',
            'specialty': '시장 요약, 투자 전략',
            'order': 100,
        },
    ]
    
    created_count = 0
    updated_count = 0
    
    for data in sources_data:
        source, created = ContentSource.objects.update_or_create(
            slug=data['slug'],
            defaults=data
        )
        
        if created:
            print(f"  ✅ 생성: {source.name}")
            created_count += 1
        else:
            print(f"  🔄 업데이트: {source.name}")
            updated_count += 1
    
    print("\n" + "=" * 80)
    print(f"✅ 완료!")
    print(f"   생성: {created_count}개")
    print(f"   업데이트: {updated_count}개")
    print("=" * 80)


def init_categories():
    print("\n" + "=" * 80)
    print("📁 콘텐츠 카테고리 초기화")
    print("=" * 80)
    
    categories_data = [
        {'name': '거시경제', 'slug': 'macro-economy', 'description': '금리, 환율, GDP, 경기 사이클 등', 'order': 1},
        {'name': '종목 분석', 'slug': 'stock-analysis', 'description': '개별 종목 심층 분석', 'order': 2},
        {'name': '미국 주식', 'slug': 'us-stocks', 'description': '미국 주식시장, 빅테크 등', 'order': 3},
        {'name': '초보자', 'slug': 'beginner', 'description': '투자 입문, 기초 지식', 'order': 4},
        {'name': '기술적 분석', 'slug': 'technical', 'description': '차트, 패턴, 지표 분석', 'order': 5},
        {'name': '자산배분', 'slug': 'asset-allocation', 'description': '포트폴리오 구성, 분산 투자', 'order': 6},
        {'name': '투자 철학', 'slug': 'philosophy', 'description': '가치투자, 성장주 투자 등', 'order': 7},
        {'name': '재무제표', 'slug': 'financial-statement', 'description': '재무제표 읽기, 분석법', 'order': 8},
        {'name': '산업 분석', 'slug': 'industry', 'description': '반도체, 바이오, 금융 등 산업 이해', 'order': 9},
        {'name': '리스크 관리', 'slug': 'risk-management', 'description': '손절, 분산, 헷지 전략', 'order': 10},
    ]
    
    created_count = 0
    updated_count = 0
    
    for data in categories_data:
        category, created = ContentCategory.objects.update_or_create(
            slug=data['slug'],
            defaults=data
        )
        
        if created:
            print(f"  ✅ 생성: {category.name}")
            created_count += 1
        else:
            print(f"  🔄 업데이트: {category.name}")
            updated_count += 1
    
    print("\n" + "=" * 80)
    print(f"✅ 완료!")
    print(f"   생성: {created_count}개")
    print(f"   업데이트: {updated_count}개")
    print("=" * 80)


if __name__ == '__main__':
    init_sources()
    init_categories()
    
    print("\n" + "=" * 80)
    print("🎉 초기 데이터 입력 완료!")
    print("=" * 80)
    print("\n다음 단계:")
    print("1. Admin 페이지에서 확인: http://localhost:8000/admin/content/")
    print("2. 필요 시 소스 추가/수정")
    print("3. 콘텐츠 큐레이션 시작!")
    print("=" * 80)

