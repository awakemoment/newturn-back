# Railway 마이그레이션 수동 실행 가이드

## Railway CLI 사용 (권장)

### 1. Railway CLI 설치 (이미 완료됨)
```bash
npm i -g @railway/cli
```

### 2. 터미널에서 직접 실행

**PowerShell 또는 CMD를 열고:**

```powershell
# 1. 프로젝트 디렉토리로 이동
cd C:\projects\business\newturn-back

# 2. Railway 로그인 (브라우저가 열립니다)
railway login

# 3. 프로젝트 연결 (프롬프트에서 프로젝트 선택)
railway link

# 4. 마이그레이션 실행
railway run python manage.py migrate
```

## Railway 웹사이트 접속 문제 해결

Railway 대시보드에 접근할 수 없다면:

1. **브라우저에서 직접 접속:**
   - https://railway.app
   - 또는 https://railway.app/dashboard

2. **GitHub 계정으로 로그인:**
   - Railway는 GitHub OAuth를 사용합니다
   - GitHub 계정으로 로그인하세요

3. **프로젝트 찾기:**
   - 로그인 후 "Projects" 메뉴에서 프로젝트 선택
   - 또는 직접 URL: https://railway.app/project/{프로젝트-ID}

## Railway 대시보드에서 마이그레이션 실행

대시보드 접속 후:

1. **프로젝트 선택**
2. **서비스(Service) 선택**
3. **"Deployments" 탭** 클릭
4. **최신 배포의 "..." 메뉴** → **"Run Command"**
5. 명령 실행: `python manage.py migrate`

## 대안: 시작 스크립트 수정 (자동화)

만약 Railway CLI나 대시보드 모두 사용할 수 없다면, 시작 스크립트를 수정하여 마이그레이션을 자동으로 실행할 수 있습니다.

하지만 **Railway CLI 사용을 강력히 권장합니다** (가장 간단하고 안전함).

