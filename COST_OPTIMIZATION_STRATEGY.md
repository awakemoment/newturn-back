# 💰 Newturn 자동화 비용 최소화 전략

**작성일**: 2025.01.14  
**목적**: 데이터 수집 자동화를 최소 비용으로 구현

---

## 🎯 **비용 최소화 원칙**

1. **무료 API 우선 사용**
2. **필요한 데이터만 업데이트** (증분 업데이트)
3. **무료/저가 호스팅 활용**
4. **스케줄링 최적화** (필요할 때만 실행)
5. **캐싱으로 API 호출 최소화**

---

## 📊 **현재 비용 구조**

### **API 비용**
- ✅ EDGAR API: **$0/월** (무료)
- ✅ Yahoo Finance: **$0/월** (무료, 비공식)
- ⚠️ Polygon.io: **$0/월** (무료 플랜, 제한적) 또는 **$49/월** (Pro)
- ⚠️ OpenAI API: **~$0-50/월** (10-K 분석, 선택)

### **인프라 비용**
- ✅ Celery Worker: 서버 리소스 사용 (무료 티어 활용 가능)
- ⚠️ Redis (Celery Broker): **$0-5/월** (무료 티어 또는 서버 내장)
- ⚠️ 서버 호스팅: **$0-20/월** (Railway/Render 무료 티어 또는 유료)

### **총 예상 비용**
- **최소 구성**: **$0/월** (무료 티어만 사용)
- **권장 구성**: **$5-10/월** (Redis + 기본 서버)
- **Pro 구성**: **$54-70/월** (Polygon.io Pro + 서버)

---

## 💡 **비용 최소화 전략**

### **전략 1: 무료 API 우선 사용** ⭐⭐⭐⭐⭐

#### **주가 데이터**
```
현재: Polygon.io 무료 플랜 (5 calls/min)
문제: 전체 종목 업데이트에 시간이 너무 오래 걸림

해결책:
1. 투자 중인 종목만 업데이트 (우선순위)
2. Yahoo Finance로 백업 (Polygon.io 실패 시)
3. 주가 업데이트 빈도 최적화
```

**구현:**
```python
# apps/stocks/tasks.py
@shared_task
def update_stock_prices_optimized():
    """
    비용 최소화 주가 업데이트
    
    우선순위:
    1. 투자 중인 종목 (필수)
    2. 관심종목 (중요)
    3. 일반 종목 (선택, 캐시 활용)
    """
    from apps.accounts.models import SavingsReward
    from apps.watchlist.models import WatchlistItem
    
    # 1. 투자 중인 종목 (최우선)
    invested_stocks = SavingsReward.objects.filter(
        status='invested'
    ).values_list('stock', flat=True).distinct()
    
    # 2. 관심종목 (높은 우선순위)
    watchlist_stocks = WatchlistItem.objects.filter(
        user__is_active=True
    ).values_list('stock', flat=True).distinct()
    
    # 3. 우선순위별 업데이트
    update_stocks_prices(list(invested_stocks))  # 필수
    update_stocks_prices(list(watchlist_stocks))  # 중요
    
    # 4. 일반 종목은 캐시된 데이터 활용 (API 호출 최소화)
```

#### **재무 데이터**
```
EDGAR API: 완전 무료, Rate Limit만 준수
전략: 분기별 공시 시즌에만 업데이트 (필요할 때만)
```

---

### **전략 2: 무료/저가 호스팅 활용** ⭐⭐⭐⭐

#### **Option A: Railway 무료 티어 (추천)**
```
Redis:
- Railway Redis: $5/월 (512MB)
- 또는 Upstash Redis: 무료 티어 (10,000 commands/day)
- 또는 서버 내장 Redis (Docker)

Celery Worker:
- Railway 서버에 통합 (별도 서버 불필요)
- 또는 서버 재시작 시 Worker 자동 실행

비용: $0-5/월
```

#### **Option B: Render 무료 티어**
```
Redis:
- Render Redis: $7/월 (25MB)
- 또는 Upstash Redis: 무료

Celery Worker:
- Render Cron Jobs (무료, 제한적)
- 또는 서버에 통합

비용: $0-7/월
```

#### **Option C: 서버 내장 Redis (최소 비용)**
```
로컬 Redis (서버에 설치):
- 비용: $0/월
- 단점: 서버 재시작 시 데이터 손실 가능
- 해결: Celery Tasks를 비동기로 실행 (Redis 불필요)

비용: $0/월
```

**권장: Railway + Upstash Redis (무료) = $0/월**

---

### **전략 3: Redis 없이 실행 (최소 비용)** ⭐⭐⭐⭐⭐

Celery 없이 Django의 단순 스케줄러 사용:

```python
# 방법 1: Django-Q (SQLite 기반, Redis 불필요)
# 방법 2: APScheduler (인메모리, 서버 재시작 시 재등록)
# 방법 3: Cron Job (서버 OS 레벨, 가장 간단)
```

**구현 예시 (Cron Job):**
```python
# scripts/daily_update.py
"""
매일 실행되는 데이터 업데이트 스크립트
Cron Job으로 실행: 0 18 * * * (매일 오후 6시)
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.accounts.tasks import update_reward_prices
from apps.stocks.tasks import update_stock_prices_optimized

if __name__ == '__main__':
    # 주가 업데이트 (투자 중인 종목만)
    update_stock_prices_optimized()
    
    # 리워드 가치 업데이트
    update_reward_prices()
```

**Cron 설정 (서버):**
```bash
# crontab -e
0 18 * * * cd /path/to/project && /usr/bin/python3 scripts/daily_update.py >> logs/cron.log 2>&1
```

**비용: $0/월** (서버에 내장)

---

### **전략 4: 증분 업데이트 (API 호출 최소화)** ⭐⭐⭐⭐⭐

#### **주가 데이터**
```python
# 이미 최신 데이터가 있으면 스킵
def update_stock_price_if_needed(stock):
    latest_price = StockPrice.objects.filter(
        stock=stock
    ).order_by('-date').first()
    
    # 오늘 데이터가 이미 있으면 스킵
    if latest_price and latest_price.date == timezone.now().date():
        return
    
    # API 호출 (필요할 때만)
    update_stock_price(stock)
```

#### **재무 데이터**
```python
# 최근 90일 내 공시만 확인
def update_financial_data_incremental():
    cutoff_date = timezone.now() - timedelta(days=90)
    
    # 최근 공시된 종목만 수집
    # EDGAR API로 변경사항 확인 후 수집
```

#### **메이트 분석**
```python
# 재무 데이터 변경된 종목만 재계산
def recalculate_mate_scores_incremental():
    # 재무 데이터가 최근 90일 내 업데이트된 종목만
    changed_stocks = Stock.objects.filter(
        financials_raw__updated_at__gte=timezone.now() - timedelta(days=90)
    ).distinct()
    
    for stock in changed_stocks:
        calculate_mate_scores(stock)
```

---

### **전략 5: 스케줄링 최적화** ⭐⭐⭐⭐

#### **필요할 때만 실행**

```python
# config/settings/base.py
CELERY_BEAT_SCHEDULE = {
    # 주가 업데이트: 주 1회 (금요일 오후 6시)
    'update-stock-prices-weekly': {
        'task': 'apps.stocks.tasks.update_stock_prices_optimized',
        'schedule': crontab(hour=18, minute=0, day_of_week=5),  # 금요일
    },
    
    # 리워드 가치: 매일 (투자 중인 종목만)
    'update-reward-prices-daily': {
        'task': 'apps.accounts.tasks.update_reward_prices',
        'schedule': crontab(hour=18, minute=0),
    },
    
    # 재무 데이터: 분기 공시 시즌만 (2월, 5월, 8월, 11월)
    'update-financial-data-quarterly': {
        'task': 'apps.stocks.tasks.update_financial_data_incremental',
        'schedule': crontab(day_of_month=15, month_of_year='2,5,8,11'),
    },
}
```

**비용 절감:**
- 주가 업데이트: 매일 → 주 1회 (API 호출 85% 감소)
- 재무 데이터: 매월 → 분기별 (API 호출 75% 감소)

---

### **전략 6: 캐싱 전략** ⭐⭐⭐

#### **주가 데이터 캐싱**
```python
# Redis 캐시 (무료 티어 또는 서버 내장)
from django.core.cache import cache

def get_cached_price(stock_code):
    cache_key = f'stock_price_{stock_code}'
    price = cache.get(cache_key)
    
    if price is None:
        # API 호출
        price = fetch_price_from_api(stock_code)
        cache.set(cache_key, price, 3600)  # 1시간 캐시
    
    return price
```

#### **재무 데이터 캐싱**
- 재무 데이터는 분기별로 변경되므로 캐시 불필요 (DB에 저장)
- API 응답만 캐싱 (1시간)

---

## 🎯 **권장 구현 방안**

### **Option A: 최소 비용 ($0/월)** ⭐⭐⭐⭐⭐

**구성:**
- ✅ Cron Job (서버 OS 레벨)
- ✅ Redis 없음 (인메모리 또는 파일 기반)
- ✅ 무료 API만 사용 (EDGAR, Yahoo Finance)
- ✅ 증분 업데이트

**구현:**
```python
# scripts/daily_update.py (Cron으로 실행)
# scripts/weekly_update.py (Cron으로 실행)
# scripts/quarterly_update.py (Cron으로 실행)
```

**장점:**
- 비용 $0/월
- 구현 간단
- 서버 재시작 안정적

**단점:**
- 서버 재시작 시 스케줄 재등록 필요
- 분산 환경에서 어려움

---

### **Option B: 저비용 ($5-10/월)** ⭐⭐⭐⭐

**구성:**
- ✅ Celery + Redis (Upstash 무료 티어)
- ✅ Railway/Render 무료 티어 서버
- ✅ 무료 API 우선
- ✅ 증분 업데이트

**구현:**
```python
# Celery Beat으로 스케줄링
# Upstash Redis (무료 티어: 10,000 commands/day)
```

**장점:**
- Celery의 안정성
- 분산 환경 지원
- 서버 재시작 시 자동 복구

**단점:**
- Upstash 무료 티어 제한 (하지만 충분함)

---

### **Option C: 중간 비용 ($20-30/월)** ⭐⭐⭐

**구성:**
- ✅ Celery + Railway Redis ($5/월)
- ✅ Railway 서버 ($5-10/월)
- ✅ Yahoo Finance (무료)
- ✅ Polygon.io 무료 플랜

**장점:**
- 안정적인 인프라
- 확장성

**단점:**
- 월 $20-30 비용

---

## 📋 **구현 로드맵 (최소 비용)**

### **Phase 1: Cron Job 구현 (즉시, $0/월)**

1. **일일 업데이트 스크립트 작성**
```python
# scripts/daily_update.py
- 투자 중인 종목 주가 업데이트
- 리워드 가치 업데이트
```

2. **주간 업데이트 스크립트 작성**
```python
# scripts/weekly_update.py
- 관심종목 주가 업데이트
- 데이터 현황 확인
```

3. **분기별 업데이트 스크립트 작성**
```python
# scripts/quarterly_update.py
- 재무 데이터 수집
- 메이트 점수 재계산
```

4. **Cron 설정**
```bash
# 서버에 Cron Job 등록
0 18 * * * python scripts/daily_update.py
0 18 * * 5 python scripts/weekly_update.py
0 9 15 2,5,8,11 * python scripts/quarterly_update.py
```

---

### **Phase 2: Celery + Upstash Redis (필요 시, $0/월)**

1. **Upstash Redis 계정 생성**
   - 무료 티어: 10,000 commands/day
   - 충분함 (일일 업데이트: ~100 commands)

2. **Celery 설정 변경**
```python
# config/settings/base.py
CELERY_BROKER_URL = env('UPSTASH_REDIS_URL')  # 무료
CELERY_RESULT_BACKEND = env('UPSTASH_REDIS_URL')
```

3. **Celery Beat 스케줄 설정**
```python
CELERY_BEAT_SCHEDULE = {
    # 최적화된 스케줄
}
```

---

## 💰 **비용 비교**

| 구성 | 월 비용 | 적합성 |
|------|---------|--------|
| **Cron Job (서버 내장)** | $0 | ⭐⭐⭐⭐⭐ MVP 단계 |
| **Celery + Upstash (무료)** | $0 | ⭐⭐⭐⭐ 안정성 필요 시 |
| **Celery + Railway Redis** | $5 | ⭐⭐⭐ 확장 필요 시 |
| **Celery + 서버 (유료)** | $20-30 | ⭐⭐ 대규모 확장 시 |
| **Polygon.io Pro 포함** | +$49 | ⭐ 필요 시 |

---

## 🎯 **최종 권장 사항**

### **즉시 구현 (Phase 0A-0B): Cron Job**

**이유:**
1. ✅ 비용 $0/월
2. ✅ 구현 간단 (1-2시간)
3. ✅ MVP 단계에 충분
4. ✅ 서버 재시작 시 재등록만 하면 됨

**구현:**
- `scripts/daily_update.py` - 일일 업데이트
- `scripts/weekly_update.py` - 주간 업데이트  
- `scripts/quarterly_update.py` - 분기 업데이트
- Cron Job 설정

### **확장 시 (Phase 1+): Celery + Upstash Redis**

**이유:**
1. ✅ 여전히 $0/월 (Upstash 무료 티어)
2. ✅ 더 안정적 (서버 재시작 시 자동 복구)
3. ✅ 분산 환경 지원
4. ✅ 모니터링 가능

---

## 🚀 **즉시 실행 가능한 구현**

다음 단계로 `scripts/daily_update.py`를 작성하시겠습니까?

```python
# scripts/daily_update.py 예시 구조
1. 투자 중인 종목 주가 업데이트 (Yahoo Finance, 무료)
2. 리워드 가치 업데이트
3. 로깅
4. 에러 처리
```

**예상 소요 시간**: 30분-1시간  
**비용**: $0/월  
**효과**: 자동화 완성 + 비용 $0

---

**마지막 업데이트**: 2025.01.14

