# 📚 Newturn 프로젝트 문서 인덱스

**최종 업데이트**: 2024.11.06

---

## 🎯 **시작 전 필독**

### **1. 마스터 로드맵** ⭐⭐⭐⭐⭐
**파일**: `MASTER_ROADMAP.md`
**내용**: 전체 프로젝트 계획, 현재 위치, 다음 액션
**읽어야 할 때**: 새 세션 시작 시 항상!

### **2. SaaS 제품 명세서** ⭐⭐⭐⭐⭐
**파일**: `SAAS_PRODUCT_SPEC.md`
**내용**: SaaS 제품 상세 스펙, 개발 로드맵, 수익 모델
**읽어야 할 때**: 제품 개발 시, 기능 기획 시

### **3. 콘텐츠 전략** ⭐⭐⭐⭐⭐
**파일**: `CONTENT_STRATEGY.md`
**내용**: AI/반도체 콘텐츠 큐레이션 전략, 카테고리, 프로세스
**읽어야 할 때**: 콘텐츠 작성 시, 큐레이션 시

### **4. 첫 큐레이션 20개** ⭐⭐⭐⭐⭐
**파일**: `FIRST_20_CURATION.md`
**내용**: AI 10개 + 반도체 10개 콘텐츠 리스트, 큐레이터 노트 가이드
**읽어야 할 때**: 지금 당장! 큐레이터 노트 작성하기

---

## 📖 **사용자 가이드**

### **3. 빠른 시작**
**파일**: `docs/GETTING_STARTED.md`
**내용**: 개발 환경 설정, 첫 실행
**읽어야 할 때**: 처음 시작할 때

### **4. 사용자 매뉴얼**
**파일**: `docs/USER_GUIDE.md`
**내용**: 서비스 사용 방법, 메이트 설명
**읽어야 할 때**: 기능 이해할 때

---

## 🔧 **개발 문서**

### **5. 밸류에이션 기능**
**파일**: `VALUATION_FEATURES.md`
**내용**: 적정가격 계산 로직, 컨센서스
**읽어야 할 때**: 밸류에이션 수정 시

### **6. 법적 준수 가이드**
**파일**: `LEGAL_COMPLIANCE.md`
**내용**: 한국 자본시장법, E-2 비자 안전, 면책조항
**읽어야 할 때**: 콘텐츠 작성 시, 법적 문구 확인 시

### **7. Stripe 결제 연동**
**파일**: `docs/STRIPE_INTEGRATION_PLAN.md`
**내용**: 결제 시스템 구현 계획 (Phase 0A)
**읽어야 할 때**: Premium 준비할 때

### **8. Polygon 주가 API**
**파일**: `docs/POLYGON_API_SETUP.md`
**내용**: 주가 데이터 수집 설정
**읽어야 할 때**: 주가 업데이트 설정 시

---

## 📋 **체크리스트**

### **9. 아침 확인사항**
**파일**: `MORNING_CHECKLIST.md`
**내용**: 매일 확인할 것들, 테스트 방법
**읽어야 할 때**: 매일 아침

### **10. 배포 체크리스트**
**파일**: `DEPLOYMENT_CHECKLIST.md`
**내용**: 배포 전 확인사항
**읽어야 할 때**: 배포할 때

---

## 📊 **릴리스 노트**

### **11. 릴리스 노트**
**파일**: `RELEASE_NOTES.md`
**내용**: 버전별 변경사항
**읽어야 할 때**: 변경 이력 확인할 때

---

## 🗑️ **아카이브 (참고용)**

다음 문서들은 참고만 하세요. **MASTER_ROADMAP.md**에 통합되었습니다:

- `COMPLETION_REPORT.md` - 초기 완료 보고서
- `DATA_STRATEGY.md` - 데이터 전략 (구버전)
- `NIGHT_WORK_SUMMARY.md` - 밤샘 작업 요약
- `QUICK_START.md` - 빠른 시작 (구버전)
- `SUMMARY.md` - 프로젝트 요약 (구버전)

**삭제된 문서:**
- `EDGAR_ONLY.md` - EDGAR 전용 전략 (변경됨)
- `US_STOCKS_ONLY.md` - 미국 주식만 (변경됨)
- `SETUP.md` → `docs/GETTING_STARTED.md`로 통합
- `STRIPE_SETUP.md` → `docs/STRIPE_INTEGRATION_PLAN.md`로 통합

---

## 🎯 **빠른 참조**

### **코드 찾기:**
```
메이트 분석: core/utils/mate_engines.py
밸류에이션: core/utils/valuation_engine.py
관심종목 API: api/watchlist/views.py
스크리닝 API: api/stocks/views.py
```

### **데이터 확인:**
```bash
python scripts/check_data_status.py
```

### **스크립트:**
```bash
# 주가 수집
python scripts/collect_stock_prices.py --limit 20

# 메이트 점수 계산
python scripts/calculate_mate_scores.py

# 데이터 현황
python scripts/check_data_status.py
```

---

## 📞 **문제 해결**

### **에러 발생 시:**
1. `newturn.log` 확인
2. Django admin 확인
3. 브라우저 콘솔 확인

### **데이터 문제:**
1. `check_data_status.py` 실행
2. DB 확인 (Django admin)
3. EDGAR API 상태 확인

---

## 🔄 **정기 업데이트**

### **매주:**
- [ ] 주간 브리핑 작성 (일요일)
- [ ] 콘텐츠 큐레이션 추가
- [ ] 데이터 상태 확인

### **매월:**
- [ ] 문서 업데이트
- [ ] 성과 리뷰
- [ ] 다음 Phase 계획

---

**새 세션 시작 시 순서:**
1. `MASTER_ROADMAP.md` 읽기 (전체 현황)
2. `PHASE_0_STRATEGY.md` 읽기 (현재 전략)
3. 현재 Phase 확인
4. `MORNING_CHECKLIST.md` 실행
5. 다음 액션 진행

**Phase 0A 작업 시:**
1. `PHASE_0_STRATEGY.md` - 상세 전략
2. `LEGAL_COMPLIANCE.md` - 법적 체크
3. 브리핑 작성 → 주간 루틴
4. Learn 탭 개발 → Week 3-6

