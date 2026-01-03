# 🎯 Newturn 서비스 비전 재정의 제안서

**작성일**: 2024.11.07  
**목적**: 소액 절약 → 주식 투자 유도 + 산업군 탐색 중심의 서비스로 전환

---

## 📌 **핵심 비전 변경**

### **기존 비전:**
> "밸류에이션 도구 + 테크 산업 전문 큐레이션"

### **새 비전:**
> **"일상 소비 절약 → 소액 주식 투자 → 장기 수익 실현"**  
> 마시멜로 실험을 투자에 적용한 행동 변화 플랫폼

---

## 🎯 **1. 소액 절약 → 주식 매수 유도 시스템**

### **1-1. "오늘 아낀 돈" 추적 기능**

**목표**: 일상 소비를 절제하고 그 돈을 주식 투자로 전환하는 습관 형성

**기능 설계:**

#### **A. 소비 절약 기록 (Savings Tracker)**
```typescript
interface DailySavings {
  date: string
  amount: number  // 오늘 아낀 금액 (원)
  category: 'coffee' | 'lottery' | 'snack' | 'subscription' | 'other'
  note?: string  // "스타벅스 아메리카노 대신 집에서 커피"
  stock_target?: number  // 이 돈으로 살 종목 ID
}
```

**UI/UX:**
- 홈페이지 상단에 **"오늘 아낀 돈"** 카드
- 빠른 입력: "커피 5,000원 아꼈어요" → 버튼 클릭
- 누적 금액 표시: "이번 주: 25,000원", "이번 달: 120,000원"
- 목표 금액 설정: "50,000원 모이면 NVDA 1주 매수!"

#### **B. 소액 투자 시뮬레이션**
```typescript
interface MicroInvestment {
  savings_id: number
  stock_id: number
  purchase_price: number  // 매수 가격
  purchase_date: string
  target_price?: number  // 목표 가격 (2배 = 10,000원)
  target_date?: string  // 목표 달성 예상일
  current_value: number  // 현재 가치
  return_rate: number  // 수익률
}
```

**시나리오:**
1. 사용자: "커피 5,000원 아꼈어요" 입력
2. 시스템: "5,000원으로 살 수 있는 종목 추천" (분할 매수 가능 종목)
3. 사용자: "NVDA로 투자할래요" 선택
4. 시스템: "NVDA 1주 = $500 → 5,000원으로 0.01주 매수 가능"
5. **시뮬레이션 시작**: 실제 매수 전, 가상 포트폴리오에서 추적
6. 목표: "5,000원 → 10,000원 되면 그때 커피 사먹기!"

#### **C. 마시멜로 대시보드**
- **현재 상태**: "아낀 돈 25,000원 → NVDA 0.05주"
- **목표까지**: "10,000원 더 모으면 1주 매수 가능!"
- **수익 추적**: "현재 가치: 28,000원 (+12%)"
- **성공 스토리**: "3개월 전 5,000원 → 지금 12,000원! 🎉"

---

### **1-2. 소액 투자 추천 엔진**

**필터 조건:**
- 최소 투자 금액: 5,000원 ~ 50,000원
- 분할 매수 가능 종목 (주가가 높아도 소액 투자 가능)
- 4개 메이트 점수 70점 이상
- 목표 수익률 달성 가능성 높은 종목

**추천 로직:**
```python
def recommend_micro_investment_stocks(amount: int, target_return: float = 2.0):
    """
    소액 투자 추천
    
    amount: 투자 가능 금액 (원)
    target_return: 목표 수익률 배수 (기본 2배 = 100% 수익)
    """
    # 1. 메이트 점수 70점 이상 필터
    # 2. 현재가 대비 적정가 20% 이상 저평가
    # 3. 목표 수익률 달성 가능성 계산
    # 4. 소액 투자 가능 여부 확인 (분할 매수)
    pass
```

---

## 🔗 **2. 산업군 연관성 탐색 시스템**

### **2-1. 산업군 네트워크 맵**

**사용자 시나리오:**
> "AI에 투자하고 싶은데... AI 회사들만 보니까 전기/전력 회사도 중요하다는 걸 알았어. 냉각시스템 관련 종목은 뭐가 있지?"

**기능 설계:**

#### **A. 산업군 연관 그래프**
```typescript
interface IndustryNode {
  id: string  // "ai", "semiconductor", "power"
  name: string
  stocks: Stock[]
  related_industries: {
    industry_id: string
    relationship: 'supplier' | 'customer' | 'complement' | 'substitute'
    strength: number  // 0-1
  }[]
}
```

**예시 관계:**
- **AI** → (supplier) → **반도체** (GPU 칩 공급)
- **AI** → (supplier) → **전력/냉각** (데이터센터 전력/냉각)
- **AI** → (customer) → **클라우드** (AI 서비스 제공)
- **반도체** → (supplier) → **반도체 장비** (ASML, Lam Research)

#### **B. "이 산업과 연관된 종목" 탐색**
- 종목 상세 페이지에 **"연관 산업군"** 섹션 추가
- 예: NVDA 클릭 → "AI", "반도체", "클라우드" → 각 산업군 클릭 → 관련 종목 리스트
- 각 종목의 **4개 메이트 점수** 함께 표시

#### **C. 산업군 스크리닝**
- 기존 스크리닝 페이지에 **"산업군별 탐색"** 탭 추가
- AI → 전기/전력 → 냉각시스템 → 관련 종목 필터링
- 산업군 내 종목들의 메이트 점수 비교

---

### **2-2. 산업군 데이터 모델 확장**

**현재 상태:**
- `Stock` 모델에 `sector`, `industry` 필드만 있음 (단순 문자열)

**개선 방안:**

```python
# apps/stocks/models.py

class Industry(models.Model):
    """산업군 마스터"""
    code = models.CharField(max_length=50, unique=True)  # "ai", "semiconductor"
    name = models.CharField(max_length=200)  # "인공지능", "반도체"
    description = models.TextField(blank=True)
    parent_industry = models.ForeignKey('self', null=True, blank=True)  # 계층 구조
    order = models.IntegerField(default=0)
    
class IndustryRelationship(models.Model):
    """산업군 간 관계"""
    from_industry = models.ForeignKey(Industry, related_name='outgoing_relations')
    to_industry = models.ForeignKey(Industry, related_name='incoming_relations')
    relationship_type = models.CharField(
        max_length=20,
        choices=[
            ('supplier', '공급자'),
            ('customer', '고객'),
            ('complement', '보완재'),
            ('substitute', '대체재'),
            ('related', '관련'),
        ]
    )
    strength = models.FloatField(default=0.5)  # 0-1
    description = models.TextField(blank=True)

class StockIndustry(models.Model):
    """종목-산업군 매핑 (다대다)"""
    stock = models.ForeignKey(Stock, related_name='industries')
    industry = models.ForeignKey(Industry, related_name='stocks')
    is_primary = models.BooleanField(default=False)  # 주 산업군 여부
    weight = models.FloatField(default=1.0)  # 해당 산업군에서의 비중
```

---

## 🏢 **3. 회사 이해 강화 (Company Discovery)**

### **3-1. 주요 제품군 표시**

**사용자 니즈:**
> "도대체 뭐 하는 회사야? 주요 제품이 뭐지?"

**기능 설계:**

#### **A. 제품군 정보 (10-K에서 추출)**
```python
# apps/stocks/models.py

class StockProduct(models.Model):
    """종목의 주요 제품/서비스"""
    stock = models.ForeignKey(Stock, related_name='products')
    product_name = models.CharField(max_length=200)  # "iPhone", "AWS"
    product_category = models.CharField(max_length=100)  # "스마트폰", "클라우드 서비스"
    revenue_contribution = models.FloatField(null=True, blank=True)  # 매출 기여도 (%)
    description = models.TextField(blank=True)
    source = models.CharField(max_length=50, default='10-K')  # 데이터 출처
```

**UI:**
- 종목 상세 페이지 상단에 **"주요 제품/서비스"** 카드
- 예: AAPL → "iPhone (60%), Services (20%), Mac (10%), iPad (8%)"
- 각 제품 클릭 → 해당 제품군 관련 종목 추천

#### **B. "이 제품과 유사한 회사" 추천**
- 제품군 기반 유사 종목 발견
- 예: "iPhone" → 삼성전자, 샤오미 등 스마트폰 제조사
- 각 종목의 메이트 점수 비교

---

### **3-2. 산업군 내 숨은 보석 발견**

**사용자 니즈:**
> "엔터에 관심이 있는데 내가 아는 종목은 소수야. 생각보다 좋은 엔터 기업도 발견하고 싶어."

**기능 설계:**

#### **A. 산업군 내 메이트 점수 랭킹**
- 산업군 선택 → 해당 산업군 내 모든 종목의 **4개 메이트 점수** 표시
- 정렬: 평균 점수, 특정 메이트 점수
- 필터: 점수 70점 이상만 보기

#### **B. "놓치기 쉬운 우량주" 추천**
```python
def find_hidden_gems(industry_id: str, min_score: int = 70):
    """
    산업군 내에서 잘 알려지지 않았지만 메이트 점수가 높은 종목 발견
    """
    # 1. 해당 산업군 종목 필터
    # 2. 메이트 평균 점수 70점 이상
    # 3. 시가총액이 상대적으로 작은 종목 (숨은 보석)
    # 4. 최근 주가 상승률이 낮은 종목 (아직 발견 안 됨)
    pass
```

**UI:**
- 산업군 페이지에 **"숨은 보석"** 섹션
- "이 산업에서 점수는 높은데 아직 주목받지 않은 종목"

---

## ⏰ **4. 투자 기간 & 목표 수익률 설정**

### **4-1. 투자 목표 설정**

**사용자 니즈:**
> "지금은 항상 단기 느낌. 적정 투자 기간과 목표 수익률이 있으면, 내가 가진 돈을 가지고 있을 수 있는 기간 만큼 중에서 목표 수익률을 생각해서 투자할 수 있을 것 같아."

**기능 설계:**

#### **A. 투자 목표 모델**
```python
# apps/analysis/models.py

class InvestmentGoal(models.Model):
    """투자 목표"""
    user = models.ForeignKey(User, related_name='investment_goals')
    stock = models.ForeignKey(Stock, related_name='goals')
    
    # 투자 정보
    investment_amount = models.DecimalField(max_digits=15, decimal_places=2)  # 투자 금액
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2, null=True)  # 매수 가격
    purchase_date = models.DateField(null=True, blank=True)
    
    # 목표 설정
    target_return_rate = models.FloatField()  # 목표 수익률 (%)
    target_price = models.DecimalField(max_digits=15, decimal_places=2, null=True)  # 목표 가격
    target_date = models.DateField()  # 목표 달성일
    holding_period_months = models.IntegerField()  # 보유 기간 (개월)
    
    # 현재 상태
    current_price = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    current_value = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    current_return_rate = models.FloatField(null=True)
    days_remaining = models.IntegerField(null=True)
    
    # 메모
    thesis = models.TextField(blank=True)  # 투자 논리
    risk_factors = models.TextField(blank=True)  # 리스크 요소
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_achieved = models.BooleanField(default=False)
    achieved_at = models.DateTimeField(null=True, blank=True)
```

#### **B. 목표 기반 종목 추천**
```python
def recommend_stocks_by_goal(
    target_return: float,
    holding_period_months: int,
    investment_amount: float
):
    """
    목표 수익률과 보유 기간에 맞는 종목 추천
    
    로직:
    1. 목표 수익률을 달성하기 위한 연평균 수익률 계산
    2. 해당 기간 동안 목표 달성 가능성이 높은 종목 필터
    3. 메이트 점수와 목표 달성 확률 종합 평가
    """
    annual_return_needed = (target_return / 100) / (holding_period_months / 12)
    
    # 메이트 점수 기반으로 목표 달성 가능성 추정
    # 예: Fisher 점수 높으면 성장주 → 단기 고수익 가능
    #     Benjamin 점수 높으면 가치주 → 안정적 수익
    pass
```

#### **C. 투자 목표 대시보드**
- **"내 투자 목표"** 페이지
- 각 목표별 진행 상황: "목표까지 23일 남음, 현재 +15%"
- 목표 달성 알림: "축하합니다! 목표 수익률 달성! 🎉"
- 실패 분석: "목표 달성 실패 → 원인 분석 (시장 하락, 종목 선택 오류 등)"

---

### **4-2. 보유 기간별 전략 추천**

**전략 분류:**
- **단기 (1-6개월)**: 성장주 중심, Fisher/Greenblatt 점수 높은 종목
- **중기 (6-18개월)**: 균형형, 4개 메이트 점수 모두 70점 이상
- **장기 (18개월+)**: 가치주 중심, Benjamin/Lynch 점수 높은 종목

**UI:**
- 스크리닝 페이지에 **"투자 기간 선택"** 필터 추가
- 선택한 기간에 맞는 메이트 점수 가중치 자동 적용

---

## 📊 **5. 통합 대시보드 재설계**

### **5-1. 홈페이지 구조 변경**

**현재:**
- 검색 중심
- 기능 하이라이트
- 루틴 안내

**변경 후:**
```
┌─────────────────────────────────────┐
│  🎯 오늘 아낀 돈: 5,000원           │
│  이번 주 누적: 25,000원             │
│  [NVDA 0.05주 매수하기]             │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  📈 내 투자 목표 (3개)              │
│  • NVDA: 목표까지 23일 (+15%)      │
│  • MSFT: 목표까지 45일 (+8%)       │
│  • AAPL: 목표까지 12일 (+22%)      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  🔍 산업군 탐색                     │
│  [AI] [반도체] [클라우드] [전력]   │
│  → AI 클릭 → 관련 종목 15개        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  💎 이번 주 발견한 숨은 보석        │
│  • ASML (반도체 장비, 점수 85)     │
│  • AVGO (네트워크 칩, 점수 82)     │
└─────────────────────────────────────┘
```

---

## 🗓️ **6. 구현 로드맵**

### **Phase 1: 소액 절약 시스템 (2주)**
- [ ] `DailySavings` 모델 생성
- [ ] 소비 절약 기록 UI
- [ ] 소액 투자 시뮬레이션 기능
- [ ] 마시멜로 대시보드

### **Phase 2: 산업군 연관성 (3주)**
- [ ] `Industry`, `IndustryRelationship` 모델 생성
- [ ] 산업군 데이터 수집/입력 (AI, 반도체, 전력, 클라우드 등)
- [ ] 산업군 네트워크 그래프 UI
- [ ] "연관 산업군" 탐색 기능
- [ ] 산업군 스크리닝 페이지

### **Phase 3: 회사 이해 강화 (2주)**
- [ ] `StockProduct` 모델 생성
- [ ] 10-K에서 제품군 정보 추출 (또는 수동 입력)
- [ ] 제품군 기반 유사 종목 추천
- [ ] "숨은 보석" 발견 기능

### **Phase 4: 투자 목표 시스템 (2주)**
- [ ] `InvestmentGoal` 모델 생성
- [ ] 투자 목표 설정 UI
- [ ] 목표 기반 종목 추천
- [ ] 투자 목표 대시보드
- [ ] 목표 달성 알림

### **Phase 5: 통합 & 개선 (1주)**
- [ ] 홈페이지 재설계
- [ ] 전체 플로우 테스트
- [ ] 사용자 피드백 수집

**총 예상 기간: 10주 (2.5개월)**

---

## 💡 **7. 차별화 포인트**

### **기존 서비스와의 차이:**
1. **소액 투자 유도**: 다른 서비스는 "돈 있는 사람" 대상, 우리는 "소액 절약 → 투자" 습관 형성
2. **산업군 네트워크**: 단순 섹터 필터가 아닌, 산업군 간 관계 탐색
3. **목표 기반 투자**: 단기/중기/장기 목표에 맞는 종목 추천
4. **숨은 보석 발견**: 잘 알려지지 않은 우량주 발굴

---

## 🎯 **8. 성공 지표 (KPI)**

1. **소액 절약 활성도**
   - 일일 절약 기록 수
   - 월간 누적 절약 금액
   - 소액 투자 전환율 (절약 → 투자)

2. **산업군 탐색**
   - 산업군 페이지 조회수
   - 연관 산업군 클릭률
   - 산업군 내 종목 발견 수

3. **투자 목표 달성**
   - 목표 설정 수
   - 목표 달성률
   - 평균 보유 기간

4. **사용자 참여**
   - 주간 활성 사용자 (WAU)
   - 평균 세션 시간
   - 기능별 사용률

---

## 📝 **9. 다음 액션**

### **즉시 시작 (이번 주):**
1. [ ] 사용자 인터뷰 결과 정리 및 우선순위 확정
2. [ ] Phase 1 (소액 절약 시스템) 상세 설계
3. [ ] `DailySavings` 모델 및 API 설계

### **다음 주:**
1. [ ] Phase 1 개발 시작
2. [ ] 산업군 데이터 수집 계획 수립

---

**작성자**: AI Assistant  
**검토 필요**: 서비스 목표, 우선순위, 구현 범위

