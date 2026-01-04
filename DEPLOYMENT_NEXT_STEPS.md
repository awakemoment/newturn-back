# ✅ 배포 성공 후 다음 단계

**배포 상태**: 성공 ✅  
**URL**: `web-production-faaf3.up.railway.app`

---

## 📋 **체크리스트**

### **1. 배포 확인 (5분)**

#### **1.1 API Health Check**

브라우저 또는 curl로 확인:

```bash
# Health Check (존재하는 경우)
curl https://web-production-faaf3.up.railway.app/api/health/

# 또는 Django Admin (존재하는 경우)
curl https://web-production-faaf3.up.railway.app/admin/
```

**예상 결과:**
- 200 OK: 정상
- 404 Not Found: 정상 (해당 엔드포인트가 없는 경우)
- 500 Internal Server Error: 환경변수 확인 필요

---

### **2. 데이터베이스 마이그레이션 (필수)** ⭐⭐⭐⭐⭐

Railway 콘솔에서 실행해야 합니다.

#### **방법 1: Railway CLI 사용 (권장)**

```bash
# Railway CLI 설치 (아직 안 하셨다면)
npm i -g @railway/cli

# 로그인
railway login

# 프로젝트 연결
cd C:\projects\business\newturn-back
railway link

# 마이그레이션 실행
railway run python manage.py migrate

# 슈퍼유저 생성 (선택사항)
railway run python manage.py createsuperuser

# 정적 파일 수집
railway run python manage.py collectstatic --noinput
```

#### **방법 2: Railway 대시보드 사용**

1. Railway 대시보드 → "web" 서비스 선택
2. **"Deployments"** 탭 → 최신 배포 클릭
3. **"View Logs"** 클릭
4. **"Open Terminal"** 버튼 클릭
5. 다음 명령어 실행:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser  # 선택사항
```

---

### **3. 환경변수 확인 (필수)** ⭐⭐⭐⭐⭐

Railway 대시보드 → "web" 서비스 → **"Variables"** 탭에서 확인:

#### **필수 환경변수 체크리스트:**

```
✅ DJANGO_SETTINGS_MODULE=config.settings.production
✅ SECRET_KEY=[설정됨]
✅ DEBUG=False
✅ DATABASE_URL=[Supabase URI]
✅ REDIS_URL=[Upstash URL]
✅ CELERY_BROKER_URL=[Upstash URL]
✅ CELERY_RESULT_BACKEND=[Upstash URL]
✅ CORS_ORIGIN=https://newturn.vercel.app
✅ ALLOWED_HOSTS=api.newturn.com,*.railway.app
```

**확인 방법:**
- Variables 탭에서 모든 변수가 설정되어 있는지 확인
- 값이 올바른지 확인 (특히 DATABASE_URL, REDIS_URL)

---

### **4. API 엔드포인트 테스트 (5분)**

배포가 성공했는지 API로 확인:

```bash
# 예시: 종목 목록 API (인증 필요할 수 있음)
curl https://web-production-faaf3.up.railway.app/api/stocks/

# 또는 브라우저에서 접속
https://web-production-faaf3.up.railway.app/api/stocks/
```

**예상 결과:**
- 200 OK + JSON 데이터: 정상 ✅
- 401 Unauthorized: 인증 필요 (정상)
- 500 Internal Server Error: 환경변수 또는 데이터베이스 문제

---

### **5. 로그 확인 (문제 발생 시)**

Railway 대시보드 → "web" 서비스 → **"Logs"** 탭:

**확인 사항:**
- 에러 메시지 확인
- 데이터베이스 연결 오류 확인
- Redis 연결 오류 확인
- 환경변수 관련 오류 확인

---

### **6. 프론트엔드 연결 (Vercel 배포 후)**

프론트엔드를 Vercel에 배포한 후:

1. Vercel 환경변수 설정:
   ```
   NEXT_PUBLIC_API_URL=https://web-production-faaf3.up.railway.app
   ```

2. 프론트엔드에서 API 호출 테스트

---

### **7. 도메인 설정 (선택사항)**

#### **백엔드 커스텀 도메인:**

1. Railway 대시보드 → "web" 서비스 → **"Settings"** → **"Domains"**
2. **"Custom Domain"** 추가: `api.newturn.com`
3. DNS 설정:
   - A 레코드 또는 CNAME 레코드 설정
   - Railway가 제공하는 DNS 정보 사용

---

## 🎯 **우선순위**

### **즉시 해야 할 것 (필수):**

1. ✅ **데이터베이스 마이그레이션** - 가장 중요!
2. ✅ **환경변수 확인** - 모든 필수 변수 설정 확인
3. ✅ **API 테스트** - 배포가 정상 작동하는지 확인

### **나중에 해도 되는 것:**

4. 슈퍼유저 생성 (관리자 페이지 접근 시 필요)
5. 정적 파일 수집 (관리자 페이지 스타일 표시)
6. 커스텀 도메인 설정
7. 프론트엔드 배포 및 연결

---

## 🚨 **문제 해결**

### **마이그레이션 실패 시:**

```bash
# 데이터베이스 연결 확인
railway run python manage.py dbshell

# 마이그레이션 상태 확인
railway run python manage.py showmigrations

# 특정 앱만 마이그레이션
railway run python manage.py migrate apps.accounts
```

### **환경변수 오류:**

- Variables 탭에서 모든 변수 재확인
- 값에 따옴표나 공백이 없는지 확인
- DATABASE_URL 형식 확인 (postgresql://로 시작)

### **500 에러 발생:**

1. Logs 탭에서 에러 메시지 확인
2. 환경변수 확인 (특히 SECRET_KEY, DATABASE_URL)
3. 데이터베이스 마이그레이션 실행 확인

---

## ✅ **완료 확인**

배포가 완전히 성공했다면:

- ✅ 배포 상태: Online
- ✅ 데이터베이스 마이그레이션: 완료
- ✅ 환경변수: 모두 설정
- ✅ API 테스트: 정상 응답

---

**다음 단계**: 프론트엔드 배포 (Vercel)

---

**마지막 업데이트**: 2025.01.14

