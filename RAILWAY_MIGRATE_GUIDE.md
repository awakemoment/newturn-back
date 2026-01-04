# Railway에서 마이그레이션 실행 가이드

## 포트 8080 확인
✅ **정상입니다!** Railway는 내부적으로 포트를 관리하며, 외부 접속은 HTTPS(443)로 자동 라우팅됩니다.
- 로그: `Listening at: http://0.0.0.0:8080` ← 정상
- 외부 접속: `https://web-production-faaf3.up.railway.app` ← 자동 라우팅

## 마이그레이션 실행 방법

### 방법 1: Railway CLI (권장 - 가장 빠름)

#### 1. Railway CLI 설치
```bash
# Windows (PowerShell)
iwr https://railway.app/install.sh | iex

# 또는 npm으로 설치
npm i -g @railway/cli
```

#### 2. 로그인
```bash
railway login
```

#### 3. 프로젝트 연결
```bash
cd C:\projects\business\newturn-back
railway link
```
프로젝트를 선택하라는 프롬프트가 나타나면 해당 프로젝트 선택

#### 4. 마이그레이션 실행
```bash
railway run python manage.py migrate
```

### 방법 2: Railway 대시보드에서 실행

1. **Railway 대시보드 접속**: https://railway.app
2. **프로젝트 선택**
3. **서비스(Service) 선택**
4. **"Deployments" 탭** 클릭
5. **최신 배포 항목 찾기**
6. **"..." (더보기)** 메뉴 클릭
7. **"Run Command"** 또는 **"Open Shell"** 선택
8. 다음 명령 실행:
   ```bash
   python manage.py migrate
   ```

**또는:**

- 서비스 페이지에서 **"Settings"** 탭
- **"Service"** 섹션에서 **"Run Command"** 또는 **"Console"** 버튼 찾기
- 명령 실행: `python manage.py migrate`

### 방법 3: 환경변수로 자동화 (장기적 해결책)

Railway의 `release` 프로세스가 작동하지 않는 경우, 시작 스크립트에서 마이그레이션을 실행할 수 있습니다.

하지만 지금은 **방법 1 (Railway CLI)** 또는 **방법 2 (대시보드)**를 사용하여 즉시 실행하는 것이 가장 빠릅니다.

## 확인

마이그레이션 실행 후:
1. `/admin/` 접속 → 로그인 페이지 표시 ✅
2. `/swagger/` 접속 → API 문서 표시 ✅
3. `/api/accounts/` 접속 → API 응답 확인 ✅

