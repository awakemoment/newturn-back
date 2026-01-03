"""큐레이션 작성 템플릿 CSV 생성 스크립트

첫 20개의 큐레이션을 빠르게 수집하기 위한 빈 템플릿을 만들어 줍니다.
실제 콘텐츠를 찾으면서 제목/링크/노트만 채워 넣으면 됩니다.

실행 예시:
    python scripts/generate_curation_template.py

결과:
    scripts/generated/curation_template_YYYYMMDD.csv 파일 생성

CSV 컬럼:
    - order: 작성 순서/번호
    - theme: 로드맵 주제 (거시경제, AI 산업 등)
    - title: 영상/기사 제목
    - url: 원본 링크
    - source_slug: admin에서 등록된 ContentSource.slug
    - category_slug: admin에서 등록된 ContentCategory.slug
    - difficulty: 1~5 (⭐~⭐⭐⭐⭐⭐)
    - tags: 쉼표로 구분된 태그
    - curator_note: 한 줄 요약/왜 유용한지
    - recommended_stocks: 티커/심볼 목록 (쉼표 구분)
    - priority/is_featured/is_required: admin 필드와 동일
    - notes: 메모
"""

from __future__ import annotations

import csv
import datetime as dt
import os
import sys
from pathlib import Path

import django


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.content.models import ContentCategory, ContentSource  # noqa: E402


PLAN = [
    {"theme": "거시경제", "category_slug": "macro-economy", "count": 4, "default_tags": ["거시", "금리"], "difficulty": 2},
    {"theme": "AI 산업", "category_slug": "industry", "count": 6, "default_tags": ["AI", "클라우드"], "difficulty": 3},
    {"theme": "반도체", "category_slug": "industry", "count": 6, "default_tags": ["Semiconductor"], "difficulty": 3},
    {"theme": "밸류에이션", "category_slug": "financial-statement", "count": 4, "default_tags": ["Valuation"], "difficulty": 2},
]

COLUMN_ORDER = [
    'order',
    'theme',
    'title',
    'url',
    'source_slug',
    'source_name_hint',
    'category_slug',
    'category_name_hint',
    'difficulty',
    'tags',
    'curator_note',
    'recommended_stocks',
    'priority',
    'is_featured',
    'is_required',
    'notes',
]


def _collect_category_hints() -> dict[str, str]:
    hints: dict[str, str] = {}
    for category in ContentCategory.objects.all().order_by('order'):
        hints[category.slug] = category.name
    return hints


def _collect_source_hints() -> dict[str, str]:
    hints: dict[str, str] = {}
    for source in ContentSource.objects.filter(is_active=True).order_by('order', 'name'):
        hints[source.slug] = source.name
    return hints


def build_rows() -> list[dict[str, str]]:
    category_hints = _collect_category_hints()
    source_hints = _collect_source_hints()

    rows: list[dict[str, str]] = []
    current_order = 1

    for plan in PLAN:
        theme = plan['theme']
        category_slug = plan['category_slug']
        default_tags = ', '.join(plan.get('default_tags', []))
        difficulty = plan.get('difficulty', 2)

        for _ in range(plan['count']):
            rows.append({
                'order': current_order,
                'theme': theme,
                'title': '',
                'url': '',
                'source_slug': '',
                'source_name_hint': '',
                'category_slug': category_slug,
                'category_name_hint': category_hints.get(category_slug, ''),
                'difficulty': difficulty,
                'tags': default_tags,
                'curator_note': '',
                'recommended_stocks': '',
                'priority': 0,
                'is_featured': 0,
                'is_required': 0,
                'notes': '',
            })
            current_order += 1

    # source 힌트는 맨 윗줄 메모로만 안내
    if rows:
        rows[0]['notes'] = (
            'source_slug은 admin에 등록된 slug 사용. 예: sampro-tv, sinsaimdang, orangeboard 등. '
            'source 목록은 scripts/generated/source_hint.txt 참고.'
        )

    return rows


def export_sources_hint(output_dir: Path) -> None:
    hints = _collect_source_hints()
    hint_file = output_dir / 'source_hint.txt'
    lines = ['활성화된 콘텐츠 소스 목록 (slug → 이름)']
    lines.append('-' * 60)
    for slug, name in hints.items():
        lines.append(f'{slug:20} {name}')

    hint_file.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    output_dir = Path(__file__).resolve().parent / 'generated'
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = build_rows()
    timestamp = dt.datetime.now().strftime('%Y%m%d')
    output_file = output_dir / f'curation_template_{timestamp}.csv'

    with output_file.open('w', newline='', encoding='utf-8-sig') as fp:
        writer = csv.DictWriter(fp, fieldnames=COLUMN_ORDER)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    export_sources_hint(output_dir)

    print('=' * 80)
    print('🎯 큐레이션 템플릿이 생성되었습니다!')
    print(f'파일 위치: {output_file}')
    print('코멘트:')
    print(' - CSV 파일을 열고 제목/링크/노트만 채운 뒤, admin에서 복사 붙여넣기 하면 됩니다.')
    print(' - source_hint.txt에서 사용 가능한 소스 slug를 확인하세요.')
    print('=' * 80)


if __name__ == '__main__':
    main()



