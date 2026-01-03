# 📱 Newturn 모바일 앱 개발 전략

**작성일**: 2025.01.14  
**목적**: Newturn 서비스를 모바일 앱(iOS/Android)으로 확장하는 전략

---

## 🎯 **모바일 앱 개발 필요성**

### **장점**
1. ✅ **사용자 접근성 향상**: 앱 아이콘 클릭 한 번으로 접근
2. ✅ **푸시 알림**: 투자 시그널, 주간 브리핑 등 실시간 알림
3. ✅ **오프라인 지원**: 캐시된 데이터 조회 가능
4. ✅ **네이티브 기능**: 바이오메트릭 인증, 주소록 연동 등
5. ✅ **사용자 유지율 증가**: 앱 설치 사용자는 웹보다 높은 재방문율

### **고려사항**
1. ⚠️ **개발 비용**: 별도 개발 필요 (웹과 공유 가능한 부분 있음)
2. ⚠️ **유지보수**: iOS/Android 두 플랫폼 지원
3. ⚠️ **배포 프로세스**: 앱스토어 심사 필요
4. ⚠️ **API 호환성**: 기존 REST API 활용 가능 (장점!)

---

## 🔧 **기술 스택 옵션**

### **Option 1: React Native (추천)** ⭐⭐⭐⭐⭐

**특징:**
- JavaScript/TypeScript 기반 (기존 프론트엔드와 유사)
- iOS/Android 동시 개발
- 코드 공유율 높음 (웹과 60-80% 공유 가능)
- 큰 커뮤니티와 생태계

**장점:**
- ✅ 기존 Next.js 개발자와 기술 스택 유사
- ✅ Expo로 빠른 프로토타이핑 가능
- ✅ Hot Reload 개발 경험 우수
- ✅ 네이티브 모듈 접근 가능

**단점:**
- ⚠️ 네이티브 기능 제한 (하지만 대부분 충분)
- ⚠️ 앱 크기 (웹뷰보다 큼)

**비용:**
- 개발: 기존 프론트엔드 개발자 활용 가능
- 배포: 무료 (앱스토어 등록비 $99/년, Play Store $25 일회)

**예상 개발 시간:**
- MVP: 2-3개월
- 풀 기능: 4-6개월

---

### **Option 2: Flutter** ⭐⭐⭐⭐

**특징:**
- Dart 언어 기반
- Google 지원
- 네이티브 성능
- 아름다운 UI

**장점:**
- ✅ 네이티브 성능
- ✅ 하나의 코드베이스로 iOS/Android
- ✅ 빠른 개발 속도
- ✅ Material Design/Cupertino 위젯

**단점:**
- ❌ Dart 언어 학습 필요 (기존 팀과 불일치)
- ❌ 커뮤니티가 React Native보다 작음

**비용:**
- 개발: Dart 개발자 필요 (또는 학습)
- 배포: 동일

**예상 개발 시간:**
- MVP: 3-4개월
- 풀 기능: 5-7개월

---

### **Option 3: Progressive Web App (PWA)** ⭐⭐⭐

**특징:**
- 기존 웹앱을 PWA로 변환
- 앱스토어 배포 없이 설치 가능
- 오프라인 지원, 푸시 알림

**장점:**
- ✅ 개발 비용 최소 (기존 웹앱 활용)
- ✅ 하나의 코드베이스
- ✅ 업데이트 즉시 반영

**단점:**
- ❌ iOS PWA 제한 (푸시 알림 등)
- ❌ 네이티브 기능 제한
- ❌ 앱스토어 배포 불가 (또는 제한적)

**비용:**
- 개발: 최소 (기존 웹앱 수정)
- 배포: 무료

**예상 개발 시간:**
- PWA 변환: 2-4주
- 풀 기능: 1-2개월

---

### **Option 4: Native (Swift/Kotlin)** ⭐⭐

**특징:**
- iOS: Swift + SwiftUI
- Android: Kotlin + Jetpack Compose

**장점:**
- ✅ 최고의 성능
- ✅ 모든 네이티브 기능 접근
- ✅ 플랫폼별 최적화

**단점:**
- ❌ 두 개의 코드베이스 유지
- ❌ 개발 시간 2배
- ❌ 비용 높음

**비용:**
- 개발: iOS 개발자 + Android 개발자
- 배포: 동일

**예상 개발 시간:**
- MVP: 4-6개월
- 풀 기능: 8-12개월

---

## 🎯 **권장 전략: React Native (Expo)**

### **이유**
1. ✅ **기존 기술 스택과 호환**: TypeScript, React 경험 활용
2. ✅ **빠른 개발**: Expo로 프로토타입 빠르게
3. ✅ **비용 효율**: 하나의 코드베이스로 두 플랫폼
4. ✅ **API 재사용**: 기존 Django REST API 그대로 활용

### **아키텍처**

```
┌─────────────────┐
│  React Native   │
│   (Expo)        │
│  iOS/Android    │
└────────┬────────┘
         │ HTTPS/REST API
         │
┌────────▼────────┐
│  Django Backend │
│  (Railway)      │
│  REST API       │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│DB     │ │ Redis │
│Supabase│ │Upstash│
└───────┘ └───────┘
```

**공유:**
- ✅ 백엔드 API: 100% 재사용
- ✅ 비즈니스 로직: API로 분리
- ✅ 디자인 시스템: 재사용 가능 (컴포넌트 스타일)

---

## 📋 **모바일 앱 기능 범위**

### **Phase 1: MVP (필수 기능)**

#### **인증**
- [ ] 이메일/소셜 로그인 (Kakao, Google)
- [ ] 토큰 기반 인증
- [ ] 자동 로그인 (토큰 저장)

#### **홈 대시보드**
- [ ] 투자 현황 요약
- [ ] Top Picks (주목 종목)
- [ ] 최근 조회 종목

#### **종목 검색/상세**
- [ ] 종목 검색
- [ ] 종목 상세 정보
- [ ] 재무 데이터 (차트)
- [ ] 메이트 분석 (4개 메이트 점수)
- [ ] 10-K 인사이트 (티어별)

#### **스크리닝**
- [ ] 필터링 (시가총액, 섹터 등)
- [ ] 종목 리스트 (카드/리스트 뷰)
- [ ] 정렬 (메이트 점수, 시가총액 등)

#### **포트폴리오**
- [ ] 포트폴리오 목록
- [ ] 포트폴리오 상세
- [ ] 종목 추가/제거
- [ ] 수익률 계산

#### **프로필/설정**
- [ ] 사용자 프로필
- [ ] 구독 정보
- [ ] 알림 설정

**예상 개발 시간: 2-3개월**

---

### **Phase 2: 고급 기능**

#### **투자 시스템 (절약→투자)**
- [ ] 카테고리 통장 관리
- [ ] 은행 계좌 연동 (Plaid)
- [ ] 절약 목표 설정
- [ ] 자동 투자
- [ ] 투자 내역 조회

#### **푸시 알림**
- [ ] 투자 시그널 (Hold/Sell)
- [ ] 주간 브리핑 알림
- [ ] 포트폴리오 변화 알림

#### **오프라인 지원**
- [ ] 캐시된 데이터 조회
- [ ] 오프라인 모드 표시

#### **차트/분석**
- [ ] 인터랙티브 차트 (TradingView 또는 react-native-chart-kit)
- [ ] 재무 데이터 시각화
- [ ] 비교 분석

**예상 개발 시간: 추가 2-3개월**

---

### **Phase 3: 네이티브 기능**

#### **바이오메트릭 인증**
- [ ] Face ID / Touch ID
- [ ] 지문 인증

#### **위젯 (iOS/Android)**
- [ ] 홈 화면 위젯 (포트폴리오 요약)
- [ ] 주목 종목 위젯

#### **공유 기능**
- [ ] 종목 공유 (링크, 이미지)
- [ ] 포트폴리오 공유

#### **Siri/Google Assistant 연동**
- [ ] 음성으로 종목 조회 (선택사항)

**예상 개발 시간: 추가 1-2개월**

---

## 🛠️ **기술 스택 상세 (React Native + Expo)**

### **핵심 라이브러리**

```json
{
  "expo": "~50.0.0",
  "react": "18.2.0",
  "react-native": "0.73.0",
  "@react-navigation/native": "^6.0.0",
  "@react-navigation/stack": "^6.0.0",
  "@react-navigation/bottom-tabs": "^6.0.0",
  "axios": "^1.6.0",
  "@tanstack/react-query": "^5.0.0",  // API 상태 관리
  "zustand": "^4.4.0",  // 전역 상태 관리
  "react-native-safe-area-context": "^4.7.0",
  "expo-secure-store": "~12.7.0",  // 토큰 저장
  "expo-notifications": "~0.27.0",  // 푸시 알림
  "react-native-chart-kit": "^6.12.0",  // 차트
  "react-native-gesture-handler": "~2.14.0",
  "react-native-reanimated": "~3.6.0"
}
```

### **프로젝트 구조**

```
newturn-mobile/
├── src/
│   ├── api/              # API 클라이언트 (기존 백엔드 호출)
│   │   ├── client.ts
│   │   ├── auth.ts
│   │   ├── stocks.ts
│   │   └── portfolio.ts
│   ├── components/       # 재사용 가능한 컴포넌트
│   │   ├── StockCard.tsx
│   │   ├── MateScore.tsx
│   │   └── Chart.tsx
│   ├── screens/          # 화면 컴포넌트
│   │   ├── Home/
│   │   ├── StockDetail/
│   │   ├── Screening/
│   │   └── Portfolio/
│   ├── navigation/       # 네비게이션 설정
│   ├── store/            # Zustand 상태 관리
│   ├── hooks/            # 커스텀 훅
│   └── utils/
├── app.json              # Expo 설정
└── package.json
```

---

## 🔐 **인증 전략**

### **토큰 기반 인증 (기존 API 활용)**

```typescript
// src/api/auth.ts
import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const API_URL = 'https://api.newturn.com';

// 로그인
export async function login(email: string, password: string) {
  const response = await axios.post(`${API_URL}/api/auth/login/`, {
    email,
    password,
  });
  
  // 토큰 저장 (SecureStore)
  await SecureStore.setItemAsync('token', response.data.token);
  
  return response.data;
}

// 자동 로그인 (토큰 확인)
export async function getStoredToken() {
  return await SecureStore.getItemAsync('token');
}

// API 요청 인터셉터 (토큰 자동 추가)
axios.interceptors.request.use(async (config) => {
  const token = await getStoredToken();
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});
```

---

## 📊 **API 활용 전략**

### **기존 REST API 100% 재사용**

모바일 앱은 기존 Django REST API를 그대로 사용합니다:

```
GET  /api/stocks/              # 종목 목록
GET  /api/stocks/{id}/         # 종목 상세
GET  /api/stocks/{id}/financial/  # 재무 데이터
GET  /api/analysis/mate/{id}/  # 메이트 분석
GET  /api/portfolio/           # 포트폴리오 목록
POST /api/portfolio/           # 포트폴리오 생성
...
```

**장점:**
- ✅ 백엔드 개발 비용 0 (기존 API 활용)
- ✅ 웹/모바일 데이터 일관성
- ✅ API 버전 관리 단순화

---

## 💰 **비용 분석**

### **개발 비용**

| 항목 | React Native | Flutter | Native | PWA |
|------|--------------|---------|--------|-----|
| **초기 개발** | 2-3개월 | 3-4개월 | 4-6개월 | 1개월 |
| **유지보수** | 중간 | 중간 | 높음 | 낮음 |
| **개발자** | 1명 (React 경험) | 1명 (학습 필요) | 2명 | 기존 팀 |

### **인프라 비용**

모바일 앱 추가 시 인프라 비용 변화:

| 항목 | 현재 (웹만) | 앱 추가 후 |
|------|------------|-----------|
| **백엔드 (Railway)** | $5/월 | $5/월 (변화 없음) |
| **DB (Supabase)** | $0/월 | $0/월 (변화 없음) |
| **Redis (Upstash)** | $0/월 | $0/월 (변화 없음) |
| **프론트엔드 (Vercel)** | $0/월 | $0/월 (변화 없음) |
| **푸시 알림 서비스** | - | $0-10/월 (Expo Push) |
| **앱스토어 등록** | - | $99/년 (iOS) + $25 (Android) |

**총 비용 증가: $0-10/월 + $124/년**

---

## 🚀 **단계별 구현 계획**

### **Phase 0: 준비 단계 (1주)**

1. ✅ React Native + Expo 프로젝트 생성
2. ✅ API 클라이언트 구조 설정
3. ✅ 기본 네비게이션 설정
4. ✅ 인증 플로우 구현

### **Phase 1: MVP (2-3개월)**

1. **Week 1-2**: 인증, 홈 화면
2. **Week 3-4**: 종목 검색/상세
3. **Week 5-6**: 스크리닝
4. **Week 7-8**: 포트폴리오
5. **Week 9-10**: 프로필/설정, 테스트
6. **Week 11-12**: 앱스토어 제출 준비

### **Phase 2: 고급 기능 (2-3개월)**

1. 투자 시스템 통합
2. 푸시 알림
3. 오프라인 지원
4. 차트/분석 고도화

### **Phase 3: 네이티브 기능 (1-2개월)**

1. 바이오메트릭 인증
2. 위젯
3. 공유 기능

---

## 📱 **앱스토어 배포 전략**

### **iOS (App Store)**

**요구사항:**
- Apple Developer Program 가입 ($99/년)
- 앱 아이콘, 스플래시 화면
- Privacy Policy, Terms of Service
- 심사 가이드라인 준수

**심사 시간:** 1-3일

### **Android (Google Play Store)**

**요구사항:**
- Google Play Console 계정 ($25 일회)
- 앱 아이콘, 스플래시 화면
- Privacy Policy, Terms of Service
- 심사 가이드라인 준수

**심사 시간:** 1-7일

---

## 🎯 **권장 사항**

### **즉시 시작할 것**

1. ✅ **React Native + Expo로 시작**
   - 기존 기술 스택과 호환
   - 빠른 프로토타이핑
   - 비용 효율적

2. ✅ **MVP부터 시작**
   - 핵심 기능만 (2-3개월)
   - 사용자 피드백 수집
   - 점진적 기능 추가

3. ✅ **기존 API 활용**
   - 백엔드 개발 비용 0
   - 웹/모바일 데이터 일관성

### **나중에 고려할 것**

1. ⏳ **네이티브 기능**
   - MVP 출시 후 사용자 피드백 기반으로 추가

2. ⏳ **성능 최적화**
   - 초기에는 Expo Managed Workflow
   - 필요 시 Bare Workflow로 마이그레이션

---

## 📚 **참고 자료**

- [Expo 공식 문서](https://docs.expo.dev/)
- [React Navigation](https://reactnavigation.org/)
- [React Native 문서](https://reactnative.dev/)
- [Expo Router](https://expo.github.io/router/docs/) - 파일 기반 라우팅
- [React Query](https://tanstack.com/query/latest) - API 상태 관리

---

## 🤔 **결론**

### **추천: React Native + Expo로 시작**

**이유:**
1. ✅ 기존 기술 스택과 호환 (TypeScript, React)
2. ✅ 빠른 개발 (2-3개월 MVP)
3. ✅ 비용 효율 (하나의 코드베이스, 기존 API 활용)
4. ✅ 확장 가능 (필요 시 네이티브 모듈 추가)

**다음 단계:**
1. Expo 프로젝트 생성
2. API 클라이언트 설정
3. 인증 플로우 구현
4. 첫 화면 (홈 대시보드) 구현

---

**마지막 업데이트**: 2025.01.14

