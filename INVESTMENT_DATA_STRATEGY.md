# 📈 Newturn 투자 데이터 적재 전략

**작성일**: 2025.01.14  
**목적**: 주식 데이터, 재무 데이터, 분석 데이터 수집 및 업데이트 전략

---

## 🎯 **데이터 유형 및 출처**

### **1. 종목 기본 정보 (Stock)**
- **출처**: SEC EDGAR, NASDAQ, NYSE
- **데이터**: 종목 코드, 회사명, CIK, 시장 구분
- **업데이트**: 월 1회 (신규 상장/상장폐지)
- **현황**: ✅ 6,019개 (US)

### **2. 재무 데이터 (EDGAR Financial Data)**
- **출처**: SEC EDGAR API (무료)
- **데이터**: Revenue, OCF, FCF, CAPEX, ROE, 부채비율 등
- **형식**: 10-Q (분기), 10-K (연간)
- **업데이트**: 분기별 (공시 후 자동 수집)
- **현황**: ✅ 5,036개 종목 (83.7%), 90,978개 분기 데이터

### **3. 주가 데이터 (Stock Price)**
- **출처**: Polygon.io (유료), Yahoo Finance (무료, 제한적)
- **데이터**: 일일 종가, 거래량
- **업데이트**: 일일 (장 마감 후)
- **현황**: ⚠️ 일부 종목만 (Polygon.io 유료 전환 필요)

### **4. 메이트 분석 데이터 (Mate Analysis)**
- **출처**: 자체 계산 (재무 데이터 기반)
- **데이터**: 4개 메이트 점수 (Benjamin, Fisher, Greenblatt, Lynch)
- **업데이트**: 재무 데이터 업데이트 시 자동 재계산
- **현황**: ✅ 3,912개 종목 (65.0%), 15,648개 분석

### **5. 정성 분석 데이터 (Qualitative Analysis)**
- **출처**: 10-K 보고서 수동 분석 (AI 보조)
- **데이터**: 비즈니스 모델, 경쟁우위, 리스크, 제품별/지역별 매출
- **업데이트**: 연 1회 (10-K 발행 후)
- **현황**: ✅ 14개 핵심 종목

### **6. 발행주식수 (Shares Outstanding)**
- **출처**: EDGAR 10-K/10-Q
- **데이터**: CommonStockSharesOutstanding
- **업데이트**: 분기별 (재무 데이터 수집 시)
- **현황**: ⚠️ 10억주 하드코딩 (개선 필요)

---

## 📊 **현재 데이터 현황**

```
✅ 종목: 6,019개 (US)
✅ EDGAR: 5,036개 (83.7%)
✅ 메이트: 3,912개 (65.0%)
✅ 정성: 14개
⚠️ 주가: 일부 (Polygon.io)
⚠️ 발행주식수: 10억주 하드코딩 (개선 필요)
```

---

## 🔄 **데이터 수집 전략**

### **Phase 1: 초기 데이터 적재 (완료)**

#### **1단계: 종목 목록 수집**
```bash
# CIK 매핑 다운로드
python scripts/download_ticker_cik_mapping.py

# S&P 500 종목 수집
python scripts/collect_sp500_stocks.py

# 전체 US 종목 수집 (선택)
python scripts/collect_sp500_all.py
```

#### **2단계: 재무 데이터 수집**
```bash
# EDGAR 재무 데이터 수집 (전체)
python scripts/collect_financial_data.py

# 누락 데이터 보완
python scripts/fill_missing_data.py

# 특정 종목 수집
python scripts/collect_missing_edgar.py
```

**전략:**
- 배치 처리 (100-500개씩)
- Rate Limit 준수 (EDGAR API: 초당 10건)
- 에러 처리 및 재시도
- 진행 상황 로깅

#### **3단계: 메이트 분석 계산**
```bash
# 메이트 점수 계산 (전체)
python scripts/calculate_mate_scores.py

# 특정 종목만 계산
python scripts/run_mate_analysis.py --stock-code AAPL
```

**전략:**
- 재무 데이터 기반 자동 계산
- 4개 메이트 모두 계산
- 캐싱 (재무 데이터 변경 시만 재계산)

#### **4단계: 정성 분석 (수동/AI)**
```bash
# 10-K 분석 (AI 보조)
python scripts/ai_10k_analyzer.py --stock-code AAPL

# 분석 결과 임포트
python scripts/import_qualitative_data.py
```

**전략:**
- 핵심 종목 우선 (S&P 500 Top 50)
- AI (Claude/GPT-4)로 초기 분석
- 수동 검토 및 보완

---

### **Phase 2: 정기 업데이트 (자동화)**

#### **일일 업데이트**

**1. 주가 데이터 업데이트**
```python
# apps/accounts/tasks.py
@shared_task
def update_stock_prices():
    """매일 장 마감 후 주가 업데이트"""
    from scripts.collect_stock_prices import collect_prices_batch
    
    # 투자 중인 종목 우선 업데이트
    invested_stocks = SavingsReward.objects.filter(
        status='invested'
    ).values_list('stock__stock_code', flat=True).distinct()
    
    # 전체 종목 업데이트 (배치 처리)
    all_stocks = Stock.objects.filter(country='us')
    collect_prices_batch(all_stocks, batch_size=5)
```

**2. 투자 리워드 가치 업데이트**
```python
@shared_task
def update_reward_prices():
    """매일 주가 업데이트 후 리워드 가치 갱신"""
    rewards = SavingsReward.objects.filter(status='invested')
    for reward in rewards:
        reward.update_current_value()
```

**스케줄:**
- 시간: 매일 오후 5시 (ET, 장 마감 후)
- Celery Beat 사용

#### **분기별 업데이트**

**1. 재무 데이터 수집**
```python
@shared_task
def update_financial_data():
    """분기별 재무 데이터 업데이트"""
    from scripts.collect_financial_data import collect_for_stocks
    
    # 최근 90일 내 신규 공시 확인
    # EDGAR API로 최신 분기 데이터 수집
    collect_for_stocks()
```

**2. 메이트 분석 재계산**
```python
@shared_task
def recalculate_mate_scores():
    """재무 데이터 업데이트 후 메이트 점수 재계산"""
    from scripts.calculate_mate_scores import calculate_all
    
    # 재무 데이터 변경된 종목만 재계산
    calculate_all(force_update=False)
```

**스케줄:**
- 시간: 분기 공시 시즌 (2월, 5월, 8월, 11월)
- 주기: 공시 후 1주일마다

#### **연간 업데이트**

**1. 정성 분석 업데이트**
```python
@shared_task
def update_qualitative_analyses():
    """연간 10-K 발행 후 정성 분석 업데이트"""
    # 핵심 종목 10-K 분석
    # AI 분석 + 수동 검토
```

**스케줄:**
- 시간: 10-K 발행 시즌 (3-4월)
- 주기: 연 1회

---

## 🛠️ **데이터 수집 스크립트 전략**

### **스크립트 분류**

#### **1. 수집 스크립트 (Collect)**
- `collect_financial_data.py` - EDGAR 재무 데이터
- `collect_stock_prices.py` - 주가 데이터
- `collect_shares_outstanding.py` - 발행주식수
- `collect_missing_edgar.py` - 누락 데이터 보완

**원칙:**
- ✅ Idempotent (중복 실행 안전)
- ✅ 배치 처리 (Rate Limit 고려)
- ✅ 에러 처리 및 재시도
- ✅ 진행 상황 로깅

#### **2. 계산 스크립트 (Calculate)**
- `calculate_mate_scores.py` - 메이트 점수 계산
- `run_mate_analysis.py` - 개별 종목 분석

**원칙:**
- ✅ 재무 데이터 기반 자동 계산
- ✅ 변경된 데이터만 재계산 (최적화)
- ✅ 결과 검증

#### **3. 분석 스크립트 (Analyze)**
- `ai_10k_analyzer.py` - 10-K AI 분석
- `import_qualitative_data.py` - 정성 분석 임포트

**원칙:**
- ✅ 핵심 종목 우선
- ✅ AI + 수동 검토
- ✅ 구조화된 데이터 저장

#### **4. 검증 스크립트 (Validate)**
- `check_data_status.py` - 데이터 현황 확인
- `check_data_quality.py` - 데이터 품질 검증
- `validate_all_10k_data.py` - 10-K 데이터 검증

**원칙:**
- ✅ 정기 실행
- ✅ 자동 알림 (문제 발견 시)

---

## ⚡ **데이터 수집 최적화 전략**

### **1. Rate Limit 관리**

#### **EDGAR API**
- 제한: 초당 10건
- 전략: 배치 처리 (10개씩, 1초 간격)
- 예상 시간: 5,000개 종목 ≈ 8-10분

#### **Polygon.io API**
- 무료 플랜: 분당 5건
- 유료 플랜: 분당 200건+
- 전략: 투자 중인 종목 우선 업데이트

#### **Yahoo Finance (백업)**
- 제한: 없음 (비공식)
- 전략: Polygon.io 실패 시 사용

### **2. 배치 처리 전략**

```python
# 예시: 재무 데이터 수집
def collect_batch(stocks, batch_size=100, delay=1):
    """
    배치 처리로 데이터 수집
    
    Args:
        stocks: 수집할 종목 리스트
        batch_size: 배치 크기
        delay: 배치 간 지연 시간 (초)
    """
    for i in range(0, len(stocks), batch_size):
        batch = stocks[i:i+batch_size]
        collect_for_stocks(batch)
        time.sleep(delay)  # Rate Limit 준수
```

### **3. 증분 업데이트**

```python
# 전체 수집 대신 변경된 데이터만 업데이트
def update_changed_data():
    # 최근 90일 내 공시 확인
    # 변경된 종목만 수집
    # 메이트 점수 재계산 (변경된 종목만)
```

### **4. 캐싱 전략**

- **재무 데이터**: 분기별 (변경 없음)
- **주가 데이터**: 일일 (실시간 필요 시 API 직접 호출)
- **메이트 분석**: 재무 데이터 변경 시만 재계산

---

## 📅 **자동화 스케줄**

### **Celery Beat 설정**

```python
# config/settings/base.py
CELERY_BEAT_SCHEDULE = {
    # 매일: 주가 업데이트 (오후 5시 ET)
    'update-stock-prices': {
        'task': 'apps.accounts.tasks.update_stock_prices',
        'schedule': crontab(hour=17, minute=0),  # ET 기준
    },
    
    # 매일: 투자 리워드 가치 업데이트 (오후 5시 30분)
    'update-reward-prices': {
        'task': 'apps.accounts.tasks.update_reward_prices',
        'schedule': crontab(hour=17, minute=30),
    },
    
    # 주 1회: 데이터 현황 확인 (월요일 오전 9시)
    'check-data-status': {
        'task': 'scripts.check_data_status.main',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),
    },
    
    # 분기별: 재무 데이터 업데이트 (공시 시즌)
    'update-financial-data': {
        'task': 'scripts.collect_financial_data.main',
        'schedule': crontab(day_of_month=15, month_of_year='2,5,8,11'),
    },
}
```

---

## 🎯 **우선순위 전략**

### **1. 핵심 종목 우선**
- S&P 500 Top 50
- 투자 중인 종목
- 관심종목으로 추가된 종목

### **2. 데이터 완성도**
- EDGAR 데이터 없는 종목 → 수집
- 메이트 분석 없는 종목 → 계산
- 주가 데이터 없는 종목 → 수집

### **3. 사용자 영향**
- 투자 중인 종목 → 최우선
- 관심종목 → 높은 우선순위
- 스크리닝 결과 → 중간 우선순위

---

## 🔧 **데이터 품질 관리**

### **1. 검증 체크리스트**

```python
# scripts/check_data_quality.py
def validate_data_quality():
    """
    데이터 품질 검증
    """
    checks = [
        check_missing_financials(),      # 누락 재무 데이터
        check_invalid_prices(),          # 이상 주가
        check_missing_mate_scores(),     # 누락 메이트 분석
        check_data_consistency(),        # 데이터 일관성
    ]
    
    for check in checks:
        if not check.passed:
            send_alert(check.message)
```

### **2. 데이터 정합성**

- 재무 데이터: 분기별 연속성 확인
- 주가 데이터: 전일 대비 변동 범위 확인
- 메이트 점수: 재무 데이터 변경 시 재계산 확인

### **3. 자동 복구**

- 수집 실패: 자동 재시도 (최대 3회)
- 데이터 오류: 알림 및 수동 검토
- 누락 데이터: 자동 보완 작업 스케줄링

---

## 💰 **비용 최적화**

### **현재 비용**
- EDGAR API: 무료
- Yahoo Finance: 무료
- Polygon.io: 무료 플랜 (제한적)

### **확장 시 비용**
- Polygon.io Pro: $49/월 (분당 200건)
- OpenAI API: ~$50/월 (10-K 분석, 선택)
- 데이터 저장: DB 비용 (Supabase/AWS RDS)

### **비용 절감 전략**
1. **무료 API 우선 사용**: EDGAR, Yahoo Finance
2. **증분 업데이트**: 전체 수집 최소화
3. **캐싱**: 불필요한 API 호출 방지
4. **배치 처리**: Rate Limit 내 최대 활용

---

## 📋 **구현 로드맵**

### **Phase 0A (현재)**
- [x] 초기 데이터 적재 완료
- [x] 메이트 분석 계산
- [x] 데이터 현황 확인 스크립트
- [ ] 주가 업데이트 자동화 (Celery)
- [ ] 발행주식수 수집 개선

### **Phase 0B (1-2개월)**
- [ ] Polygon.io Pro 구독 (주가 데이터 완성)
- [ ] 자동 업데이트 스케줄 (Celery Beat)
- [ ] 데이터 품질 검증 자동화
- [ ] 핵심 종목 정성 분석 확대 (14개 → 50개)

### **Phase 1 (3-6개월)**
- [ ] 실시간 주가 업데이트 (WebSocket)
- [ ] 데이터 분석 대시보드
- [ ] 예측 모델 구축 (선택)
- [ ] 데이터 API 제공 (Enterprise)

---

## 🚨 **주의사항**

### **1. API Rate Limit**
- EDGAR: 초당 10건 준수
- Polygon.io: 플랜별 제한 확인
- Yahoo Finance: 비공식 API (불안정)

### **2. 데이터 정확성**
- EDGAR 공시 데이터: 공식 데이터이므로 신뢰
- 주가 데이터: Polygon.io 권장 (Yahoo Finance는 백업용)
- 메이트 분석: 계산 로직 정확성 검증 필요

### **3. 법적 고려사항**
- 데이터 라이선스 확인
- 재배포 제한 확인
- 개인정보 보호 (사용자 데이터와 분리)

---

## 📚 **참고 자료**

### **API 문서**
- [SEC EDGAR API](https://www.sec.gov/edgar/sec-api-documentation)
- [Polygon.io API](https://polygon.io/docs)
- [Yahoo Finance (비공식)](https://github.com/ranaroussi/yfinance)

### **스크립트 가이드**
- `scripts/check_data_status.py` - 데이터 현황 확인
- `scripts/collect_financial_data.py` - 재무 데이터 수집
- `scripts/calculate_mate_scores.py` - 메이트 점수 계산

---

**마지막 업데이트**: 2025.01.14  
**다음 리뷰**: Polygon.io Pro 전환 전

