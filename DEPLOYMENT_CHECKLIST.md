# ✅ Newturn 무료 베타 배포 체크리스트

**목표**: 무료 베타 출시 (5,000개 종목)

---

## 📊 **데이터 준비**

### **필수 (완료)**
- [x] CIK 매핑 (6,019개)
- [x] EDGAR 재무 데이터 (5,036개)
- [x] 메이트 점수 (3,912개)
- [x] 정성 분석 (14개 → 20개 목표)

### **선택 (나중에)**
- [ ] 주가 데이터 (Polygon.io) - 백그라운드 수집
- [ ] 나머지 EDGAR (외국 기업 983개) - 20-F 지원 필요

---

## 🛠️ **백엔드**

### **기능 완성도**
- [x] 종목 API (검색, 상세, 재무)
- [x] 스크리닝 API (필터, 정렬)
- [x] 스크리닝 테이블 API (최적화 완료)
- [x] 메이트 분석 API
- [x] 10-K 인사이트 API (티어 제한)
- [x] 포트폴리오 API
- [x] Hold/Sell 시그널
- [x] Stripe 통합
- [x] 인증 (Kakao, Google - 목업)

### **성능 최적화**
- [x] N+1 쿼리 해결 (select_related)
- [x] 메이트 테이블 prefetch
- [x] 페이지네이션 (50개/페이지)

### **보안**
- [x] 티어별 권한 제어 (@require_tier)
- [x] CORS 설정
- [x] AllowAny → IsAuthenticated 변경 (프로덕션)

---

## 🎨 **프론트엔드**

### **페이지 완성도**
- [x] 메인 페이지 (Top Picks 실시간)
- [x] 스크리닝 (테이블/카드 뷰)
- [x] 종목 상세 (메이트 + 10-K)
- [x] 비교 페이지
- [x] 포트폴리오 목록/상세
- [x] 로그인 페이지
- [x] 구독 페이지

### **UX 개선**
- [x] 카드 뷰 메이트 점수 표시
- [x] 테이블 뷰 점수 색상 코딩
- [x] 현금흐름 그래프 시간 순서
- [x] 로딩 스피너
- [x] 에러 처리

### **반응형**
- [x] 모바일 지원
- [x] 태블릿 지원
- [x] 데스크톱 최적화

---

## 📖 **문서**

- [x] README.md
- [x] USER_GUIDE.md
- [x] RELEASE_NOTES.md
- [x] POLYGON_API_SETUP.md
- [x] API 문서 (Swagger)

---

## 🧪 **테스트**

### **기능 테스트**
- [ ] 메인 페이지 로딩
- [ ] 스크리닝 테이블 뷰
- [ ] 스크리닝 카드 뷰
- [ ] 종목 상세 (재무 + 메이트)
- [ ] 10-K 인사이트 (Standard)
- [ ] 포트폴리오 CRUD
- [ ] 비교 기능
- [ ] 검색

### **성능 테스트**
- [ ] 테이블 로딩 시간 (<2초)
- [ ] 종목 상세 로딩 (<500ms)
- [ ] 메이트 점수 계산 속도

### **보안 테스트**
- [ ] 무료 유저 → 10-K 접근 차단
- [ ] 인증 없이 API 접근 (AllowAny 확인)

---

## 🚀 **배포 전 작업**

### **환경 변수**
```bash
# 프로덕션 .env
DEBUG=False
ALLOWED_HOSTS=newturn.com,www.newturn.com
DATABASE_URL=postgresql://...
STRIPE_SECRET_KEY=sk_live_xxx
POLYGON_API_KEY=xxx
```

### **DB 마이그레이션**
```bash
python manage.py migrate
python manage.py collectstatic
```

### **데이터 로드**
```bash
python scripts/download_ticker_cik_mapping.py
python scripts/collect_missing_edgar.py
python scripts/calculate_mate_scores.py
python scripts/analyze_6more_stocks.py
```

---

## 📊 **모니터링**

### **메트릭**
- [ ] API 응답 시간
- [ ] 에러율
- [ ] 사용자 수
- [ ] 인기 종목 Top 10

### **로깅**
- [ ] 에러 로그 (Sentry)
- [ ] 접속 로그
- [ ] API 호출 로그

---

## 🎯 **출시 기준**

### **필수 (Pass)**
- [x] 3,000개 이상 종목 메이트 분석
- [x] 스크리닝 테이블 작동
- [ ] 종목 상세 페이지 로딩 (<1초)
- [x] 메인 페이지 Top Picks 표시

### **권장 (Nice to Have)**
- [ ] 주가 데이터 (나중에 가능)
- [x] 20개 정성 분석
- [ ] Plaid 연동 (Phase 2)

---

## 🔥 **긴급 수정 사항**

현재 없음

---

## 📅 **릴리스 일정**

- **Beta v0.1**: 2024.11.06 (현재)
- **Beta v0.2**: 2024.11.20 (주가 + 500개 정성)
- **v1.0**: 2024.12.15 (Plaid + 결제)

---

**마지막 업데이트**: 2024.11.06 16:30 KST

