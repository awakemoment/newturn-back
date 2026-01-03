# 💾 Newturn 데이터 보존 및 데이터 비즈니스 전략

**작성일**: 2025.01.14  
**목적**: 데이터 보존 전략 및 데이터 판매 비즈니스 고려한 인프라 설계

---

## 🎯 **핵심 전략: 데이터 보존 최우선**

### **원칙**
- ✅ **모든 데이터 보존**: 주가, 재무, 분석 데이터 완전 보존
- ✅ **히스토리 완전성**: 시간이 지날수록 데이터 가치 증가
- ✅ **데이터 판매 준비**: API/Export 형태로 데이터 제공 가능한 구조

---

## 📊 **데이터 증가 예측 (보존 전략)**

### **초기 데이터 크기**
```
종목 데이터:        0.5 MB
재무 데이터:       20 MB
메이트 분석:        2 MB
주가 데이터 (5년): 315 MB
10-K 인사이트:     10 MB
개인 데이터 (1명):  2.64 MB
─────────────────────────
초기 총계:        350 MB
```

### **연간 증가량 (모든 데이터 보존)**
```
재무 데이터:        4 MB/년
주가 데이터:       63 MB/년 (5,000개 종목 × 252일)
메이트 분석:       30 MB/년 (월별 재계산, 이력 보존)
10-K 인사이트:     40 MB/년 (분기별 생성)
개인 데이터:       2 MB/년
─────────────────────────
연간 증가:        139 MB/년
```

### **장기 데이터 크기 예측**

| 연도 | 데이터 크기 | 누적 증가 |
|------|------------|----------|
| 초기 | 350 MB | - |
| 1년 | 489 MB | +139 MB |
| 2년 | 628 MB | +278 MB |
| 3년 | 767 MB | +417 MB |
| 4년 | 906 MB | +556 MB |
| 5년 | 1,045 MB | +695 MB |
| 10년 | 1,740 MB | +1,390 MB |
| 20년 | 3,130 MB | +2,780 MB |

---

## 💰 **인프라 재검토 (데이터 보존 + 판매 준비)**

### **시나리오 1: Supabase Free → Pro (권장)** ⭐⭐⭐⭐⭐

#### **초기 (1-3년): Supabase Free (500MB)**
```
Frontend: Vercel (무료)
Backend: Railway ($5/월)
Database: Supabase Free (500MB)
Redis: Upstash (무료)
총 비용: $5/월

사용 기간: 약 3-4년
```

#### **확장 (3년 후): Supabase Pro ($25/월)**
```
Frontend: Vercel (무료)
Backend: Railway ($5/월)
Database: Supabase Pro ($25/월, 8GB)
Redis: Upstash (무료)
총 비용: $30/월

사용 기간: 20년 이상 (8GB = 8,000MB)
```

**전략:**
- ✅ 초기 비용 최소화 ($5/월)
- ✅ 필요 시 업그레이드 (데이터 400MB 도달 시)
- ✅ 8GB면 20년 이상 충분

---

### **시나리오 2: 초기부터 Supabase Pro** ⭐⭐⭐⭐

```
Frontend: Vercel (무료)
Backend: Railway ($5/월)
Database: Supabase Pro ($25/월, 8GB)
Redis: Upstash (무료)
총 비용: $30/월

장점:
- ✅ 데이터 걱정 없음 (20년 이상)
- ✅ Point-in-Time Recovery (PITR)
- ✅ 더 나은 성능
- ✅ 데이터 판매 준비 완료

단점:
- ⚠️ 초기 비용 증가 ($25/월)
```

---

### **시나리오 3: PostgreSQL 직접 관리 (고급)** ⭐⭐⭐

#### **Railway PostgreSQL**
```
Frontend: Vercel (무료)
Backend: Railway ($5/월)
Database: Railway PostgreSQL ($5/월, 256GB)
Redis: Upstash (무료)
총 비용: $10/월

장점:
- ✅ 매우 큰 용량 (256GB)
- ✅ 저렴한 비용
- ✅ Railway 통합 관리

단점:
- ⚠️ 백업 수동 설정 필요
- ⚠️ 관리 복잡도 증가
```

**비용 비교:**
- Railway PostgreSQL: $5/월 (256GB)
- Supabase Pro: $25/월 (8GB)

**결론**: 데이터가 커지면 Railway PostgreSQL이 더 비용 효율적 (하지만 관리 복잡도 증가)

---

## 📈 **데이터 판매 비즈니스 준비**

### **데이터 상품화 전략**

#### **1. API 서비스 (API-as-a-Service)**
```
제공 데이터:
- 재무 데이터 API
- 주가 데이터 API
- 메이트 분석 API
- 10-K 인사이트 API

가격 모델:
- Free: 100 requests/day
- Pro: $49/월 (1,000 requests/day)
- Enterprise: $299/월 (무제한)
```

#### **2. 데이터 Export 서비스**
```
제공 형태:
- Excel/CSV 다운로드
- JSON API
- 데이터베이스 덤프

가격 모델:
- 재무 데이터: $99/년
- 주가 데이터: $199/년
- 전체 데이터: $499/년
```

#### **3. 분석 리포트 서비스**
```
제공 내용:
- 산업별 분석 리포트
- 메이트 점수 트렌드 분석
- 재무 데이터 비교 분석

가격 모델:
- 월간 리포트: $29/월
- 연간 리포트: $299/년
```

---

## 🏗️ **데이터 판매 아키텍처 (미래 확장)**

### **Phase 1: 현재 (데이터 수집)**
```
┌─────────────────┐
│   Backend API   │
│   (Django)      │
│   Railway       │
└────────┬────────┘
         │
┌────────▼────────┐
│   PostgreSQL    │
│   (Supabase)    │
│   모든 데이터   │
└─────────────────┘
```

### **Phase 2: 데이터 판매 추가 (확장)**
```
┌─────────────────┐
│   Backend API   │
│   (Django)      │
│   Railway       │
├─────────────────┤
│  Data API       │
│  (별도 엔드포인트)│
└────────┬────────┘
         │
┌────────▼────────┐
│   PostgreSQL    │
│   (Supabase/Railway)│
│   모든 데이터   │
└─────────────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│ 캐시  │ │ 로깅  │
│Redis  │ │Sentry │
└───────┘ └───────┘
```

### **Phase 3: 데이터 플랫폼 (대규모)**
```
┌─────────────────┐
│   Data API      │
│   (FastAPI)     │
│   별도 서비스   │
└────────┬────────┘
         │
┌────────▼────────┐
│   Read Replica  │
│   (읽기 전용)   │
└────────┬────────┘
         │
┌────────▼────────┐
│   PostgreSQL    │
│   (Master)      │
│   모든 데이터   │
└─────────────────┘
```

---

## 📋 **데이터 구조 최적화 (보존 + 판매)**

### **1. 데이터 정규화**

#### **현재 구조 (이미 잘 설계됨)**
```python
# 재무 데이터: 분기별 저장
StockFinancialRaw(
    stock, disclosure_year, disclosure_quarter,
    revenue, ocf, capex, ...
)

# 주가 데이터: 일별 저장
StockPrice(
    stock, date,
    open_price, high_price, low_price, close_price, volume
)

# 메이트 분석: 계산 시점별 저장 (히스토리 보존)
MateAnalysis(
    stock, mate_type, calculated_at,
    score, summary, reason, ...
)
```

**장점:**
- ✅ 시간별 데이터 추적 가능
- ✅ 트렌드 분석 가능
- ✅ 데이터 판매 시 가치 높음

---

### **2. 데이터 인덱싱 (성능 최적화)**

```python
# models.py
class StockPrice(models.Model):
    stock = models.ForeignKey(Stock, ...)
    date = models.DateField(db_index=True)  # ✅ 인덱스
    
    class Meta:
        indexes = [
            models.Index(fields=['stock', 'date']),  # ✅ 복합 인덱스
            models.Index(fields=['date']),  # ✅ 날짜 범위 쿼리용
        ]
```

**데이터 판매 시 중요:**
- ✅ 빠른 쿼리 응답 (API 성능)
- ✅ 대량 데이터 Export 성능

---

### **3. 데이터 버전 관리**

#### **메이트 분석 히스토리 보존**
```python
# 현재: MateAnalysis (최신만)
# 개선: MateAnalysisHistory (모든 계산 이력)

class MateAnalysisHistory(models.Model):
    stock = models.ForeignKey(Stock, ...)
    mate_type = models.CharField(...)
    calculated_at = models.DateTimeField()
    score = models.IntegerField()
    # ... 분석 결과
    
    class Meta:
        indexes = [
            models.Index(fields=['stock', 'calculated_at']),
        ]
```

**데이터 판매 가치:**
- ✅ "메이트 점수 변화 추적" 상품
- ✅ "과거 분석 vs 현재 분석" 비교 데이터

---

## 💾 **데이터 백업 전략**

### **Supabase Free (초기)**
- ✅ 자동 백업 (7일 보관)
- ✅ 수동 백업 가능 (pg_dump)

### **Supabase Pro (업그레이드 후)**
- ✅ Point-in-Time Recovery (PITR)
- ✅ 7일 백업 보관
- ✅ 데이터 복구 용이

### **추가 백업 (데이터 비즈니스 준비)**

#### **정기 데이터 Export**
```python
# scripts/export_data_for_backup.py
# 월 1회 전체 데이터 Export (S3 또는 로컬)

def export_financial_data():
    """재무 데이터 Export (CSV)"""
    data = StockFinancialRaw.objects.all()
    df = pd.DataFrame(list(data.values()))
    df.to_csv(f'backup/financial_data_{date}.csv')
    
def export_stock_prices():
    """주가 데이터 Export (Parquet - 압축 효율)"""
    data = StockPrice.objects.all()
    df = pd.DataFrame(list(data.values()))
    df.to_parquet(f'backup/stock_prices_{date}.parquet')
```

**백업 저장소:**
- AWS S3: $0.023/GB/월
- 1GB 백업: $0.023/월 (~₩30/월)

---

## 🎯 **최종 권장 인프라 (데이터 보존 + 판매 준비)**

### **Option 1: 단계적 확장 (권장)** ⭐⭐⭐⭐⭐

#### **Phase 1 (1-3년): 최소 비용**
```
Frontend: Vercel (무료)
Backend: Railway ($5/월)
Database: Supabase Free (500MB)
Redis: Upstash (무료)
총 비용: $5/월

사용 기간: 약 3-4년 (데이터 500MB 도달 시)
```

#### **Phase 2 (3년 후): Pro 업그레이드**
```
Frontend: Vercel (무료)
Backend: Railway ($5/월)
Database: Supabase Pro ($25/월, 8GB)
Redis: Upstash (무료)
총 비용: $30/월

사용 기간: 20년 이상
```

**전략:**
- ✅ 초기 비용 최소화
- ✅ 데이터 판매 시작 시점에 맞춰 업그레이드
- ✅ 8GB면 20년 이상 충분

---

### **Option 2: 초기부터 Pro (안정성 우선)** ⭐⭐⭐⭐

```
Frontend: Vercel (무료)
Backend: Railway ($5/월)
Database: Supabase Pro ($25/월, 8GB)
Redis: Upstash (무료)
총 비용: $30/월

장점:
- ✅ 데이터 걱정 없음 (20년 이상)
- ✅ PITR (데이터 복구 안전)
- ✅ 데이터 판매 준비 완료
- ✅ 성능 우수

단점:
- ⚠️ 초기 비용 증가 ($25/월)
```

---

### **Option 3: Railway PostgreSQL (장기 최적)** ⭐⭐⭐

```
Frontend: Vercel (무료)
Backend: Railway ($5/월)
Database: Railway PostgreSQL ($5/월, 256GB)
Redis: Upstash (무료)
총 비용: $10/월

장점:
- ✅ 매우 큰 용량 (256GB, 100년 이상)
- ✅ 저렴한 비용 ($5/월)
- ✅ 데이터 판매 대량 처리 가능

단점:
- ⚠️ 백업 수동 설정
- ⚠️ 관리 복잡도 증가
- ⚠️ PITR 없음 (수동 백업 필요)
```

---

## 📊 **비용 비교표 (20년 기준)**

| 옵션 | 초기 비용 | 3년 후 | 20년 총 비용 | 용량 |
|------|----------|--------|-------------|------|
| **Option 1** | $5/월 | $30/월 | $3,420 | 8GB (20년 이상) |
| **Option 2** | $30/월 | $30/월 | $7,200 | 8GB (20년 이상) |
| **Option 3** | $10/월 | $10/월 | $2,400 | 256GB (100년 이상) |

**비용 효율: Option 3 > Option 1 > Option 2**  
**관리 편의: Option 2 > Option 1 > Option 3**

---

## 🎯 **최종 권장: Option 1 (단계적 확장)**

### **이유:**
1. ✅ **초기 비용 최소화**: $5/월 (3년간 $180)
2. ✅ **데이터 판매 시작 시점에 맞춰 업그레이드**: 수익 발생 시
3. ✅ **충분한 용량**: Supabase Pro 8GB = 20년 이상
4. ✅ **관리 편의**: Supabase 자동 백업, PITR
5. ✅ **확장 가능**: 필요 시 Railway PostgreSQL로 마이그레이션

### **마이그레이션 경로:**
```
Supabase Free (1-3년)
    ↓
Supabase Pro (3-20년)
    ↓
Railway PostgreSQL (20년 후, 필요 시)
```

---

## 📋 **데이터 판매 준비 체크리스트**

### **즉시 준비 (현재)**
- [x] 데이터 구조 설계 (완료)
- [x] 데이터 수집 시스템 (완료)
- [ ] 데이터 Export 스크립트 작성
- [ ] 데이터 품질 검증

### **데이터 판매 시작 전 (Phase 2)**
- [ ] API 문서 작성 (Swagger)
- [ ] API Rate Limiting 구현
- [ ] 데이터 라이선스 정책 수립
- [ ] 결제 시스템 연동 (Stripe)
- [ ] 데이터 사용량 모니터링

### **대규모 데이터 판매 (Phase 3)**
- [ ] Read Replica 구성 (성능)
- [ ] 캐싱 레이어 추가
- [ ] 데이터 파이프라인 자동화
- [ ] 분석 리포트 자동 생성

---

## 💡 **데이터 비즈니스 아이디어**

### **1. 재무 데이터 API**
- **타겟**: 금융 앱, 투자 분석 도구
- **가격**: $99-299/월
- **제공**: REST API, Webhook

### **2. 주가 데이터 히스토리**
- **타겟**: 백테스팅 도구, 알고리즘 트레이딩
- **가격**: $199-499/월
- **제공**: CSV, JSON, Database Dump

### **3. 메이트 분석 리포트**
- **타겟**: 개인 투자자, 투자 클럽
- **가격**: $29-99/월
- **제공**: PDF 리포트, Excel

### **4. 산업별 분석 데이터**
- **타겟**: 컨설팅, 리서치 회사
- **가격**: $499-999/월
- **제공**: 맞춤 분석 리포트

---

**마지막 업데이트**: 2025.01.14

