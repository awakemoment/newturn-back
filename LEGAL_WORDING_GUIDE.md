# 📝 법적 준수 문구 가이드

**즉시 적용 필수!** ⚖️

---

## ❌ **사용 금지 문구**

```
추천합니다
추천 종목
Top Picks
매수하세요
매도하세요
사세요 / 파세요
강력 매수
투자 권유
이 종목을 담으세요
```

---

## ✅ **안전한 대체 문구**

### **추천 → 분석/주목**
```
Before: "베니의 추천"
After:  "베니 관점 분석"

Before: "추천 종목"
After:  "주목 종목" / "분석 대상"

Before: "Top Picks"
After:  "주목 종목" / "우량주 분석"
```

### **매수/매도 → 저평가/고평가**
```
Before: "강력 매수"
After:  "20% 이상 저평가"

Before: "매수"
After:  "10% 이상 저평가"

Before: "매수 시그널"
After:  "저평가 알림"

Before: "매도 고려"
After:  "20% 이상 고평가"

Before: "매도 시그널"
After:  "고평가 알림"
```

### **투자 조언 → 분석 결과**
```
Before: "투자 추천"
After:  "분석 결과"

Before: "투자 컨센서스"
After:  "분석 종합"

Before: "추천: 매수"
After:  "분석: 저평가 구간"
```

---

## 📋 **백엔드 API 응답 수정**

### **api/watchlist/views.py:**
```python
# Before
recommendation = "🟢 강력 매수 (20% 이상 저평가)"

# After
recommendation = "🟢 20% 이상 저평가 (참고)"
```

### **core/utils/valuation_engine.py:**
```python
# Before
if gap_ratio <= -20:
    recommendation = "🟢 강력 매수 (20% 이상 저평가)"

# After
if gap_ratio <= -20:
    recommendation = "🟢 20% 이상 저평가 (매우 저평가)"
```

---

## 🎨 **프론트엔드 UI 수정**

### **1. 메인 페이지:**
```tsx
// Before
<h2>메이트별 Top Pick</h2>
<p>4명의 투자 전설이 선택한 최고의 종목</p>

// After
<h2>메이트별 주목 종목</h2>
<p>4가지 투자 관점에서 분석한 우량 종목 (참고용)</p>
```

### **2. 스크리닝:**
```tsx
// Before
{ id: 1, icon: '🎩', name: '베니의 추천', desc: '안전마진' }

// After
{ id: 1, icon: '🎩', name: '베니 관점 우량주', desc: '안전마진 분석' }
```

### **3. 관심종목:**
```tsx
// Before
<h3>🟢 매수 시그널</h3>
signal_data['signal'] = '강력 매수'

// After
<h3>🟢 저평가 알림</h3>
signal_data['signal'] = '20% 이상 저평가'
```

### **4. 밸류에이션 대시보드:**
```tsx
// Before
<h2>투자 컨센서스</h2>
"🟢 만장일치 매수!"

// After
<h2>분석 종합</h2>
"🟢 4개 관점 모두 저평가"
```

---

## 📄 **면책 조항 (필수)**

### **모든 페이지에 Footer 추가:**
```tsx
import DisclaimerFooter from '@/components/DisclaimerFooter'

<div className="min-h-screen flex flex-col">
  {/* Main Content */}
  ...
  
  {/* Footer */}
  <DisclaimerFooter />
</div>
```

---

## 🎯 **수정 체크리스트**

### **백엔드:**
- [ ] `api/watchlist/views.py` - _get_recommendation()
- [ ] `core/utils/valuation_engine.py` - recommendation 문구
- [ ] `scripts/add_aapl_sample_contents.py` - 큐레이터 노트

### **프론트엔드:**
- [ ] `app/page.tsx` - 메인
- [ ] `app/screen/page.tsx` - 스크리닝
- [ ] `app/watchlist/page.tsx` - 관심종목
- [ ] `components/ValuationDashboard.tsx` - 밸류에이션
- [ ] `components/MateInfoModal.tsx` - 메이트 소개
- [ ] 모든 페이지에 `DisclaimerFooter` 추가

---

**이 가이드대로 수정하겠습니다!** 🚀

