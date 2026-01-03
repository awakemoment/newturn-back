# 🚀 Newturn - AI 기반 투자 지식 플랫폼

**투자 컨텍스트 + 정량 분석 + 콘텐츠 큐레이션**

---

## 📍 **빠른 시작**

### **1. 문서 읽기**
```bash
# 필독!
MASTER_ROADMAP.md        # 전체 프로젝트 계획
PROJECT_INDEX.md         # 문서 인덱스
MORNING_CHECKLIST.md     # 일일 체크리스트
```

### **2. 개발 환경 설정**
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements/base.txt

# 데이터베이스 마이그레이션
python manage.py migrate

# 서버 실행
python manage.py runserver
```

### **3. 데이터 확인**
```bash
python scripts/check_data_status.py
```

---

## 🎯 **현재 상태**

```
✅ 완료:
  - 5,036개 종목 EDGAR 데이터 (83.7%)
  - 3,912개 종목 메이트 분석 (65.0%)
  - 4개 메이트 밸류에이션 시스템
  - 관심종목 + 매수/매도 시그널
  - 메이트 소개 모달

🔄 진행 중:
  - Phase 1 (개인 사용 완성)
  - 콘텐츠 큐레이션 시스템

⏸️ 계획:
  - Phase 2-4 (검증 후)
```

---

## 📚 **핵심 기능**

### **1. 4개 메이트 밸류에이션**
- 🎩 베니 (Graham Number)
- 🌱 그로우 (DCF)
- 🔮 매직 (ROE-PBR)
- 🎯 데일리 (PEG)

### **2. 투자 컨센서스**
- 4개 메이트의 합의 제공
- 만장일치 매수/매도 신호
- 확신 있는 투자 결정

### **3. 콘텐츠 큐레이션** (개발 중)
- 양질의 유튜브, 강의 추천
- 종목별 맞춤 학습 경로
- 주간 시장 브리핑

---

## 🛠️ **기술 스택**

- **Backend**: Django 4.2, PostgreSQL
- **Frontend**: Next.js 14, TypeScript, Tailwind
- **Data**: EDGAR API, Polygon.io, Yahoo Finance
- **AI**: OpenAI GPT-4 (Phase 4)

---

## 📖 **문서**

- `MASTER_ROADMAP.md` - 전체 계획
- `PROJECT_INDEX.md` - 문서 인덱스
- `docs/GETTING_STARTED.md` - 상세 가이드
- `docs/USER_GUIDE.md` - 사용자 매뉴얼
- `VALUATION_FEATURES.md` - 밸류에이션 문서

---

## 🎯 **다음 단계**

**Phase 1 (이번 주):**
1. 발행주식수 정확도 (EDGAR)
2. 콘텐츠 큐레이션 시스템
3. 모바일 반응형

**자세한 내용**: `MASTER_ROADMAP.md` 참조

---

## 📞 **지원**

- GitHub: [링크]
- Email: [이메일]
- Docs: `PROJECT_INDEX.md`

---

**만든 사람**: [이름]
**최종 업데이트**: 2024.11.06
