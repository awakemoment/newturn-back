# Railway 대시보드 접근 문제 해결

## 문제
Railway 대시보드에 접근할 수 없어 마이그레이션을 실행할 수 없음.

## 해결 방법

### 1. Railway 웹사이트 직접 접속
- https://railway.app
- 또는 https://railway.app/dashboard

### 2. GitHub OAuth 로그인
Railway는 GitHub 계정으로 로그인합니다:
1. Railway 웹사이트 접속
2. "Login with GitHub" 클릭
3. GitHub 계정 인증
4. 프로젝트 선택

### 3. 프로젝트 찾기
- 로그인 후 "Projects" 메뉴에서 "newturn-backend" 프로젝트 찾기
- 또는 최근 프로젝트 목록에서 선택

### 4. 대시보드에서 마이그레이션 실행
1. 프로젝트 선택
2. "web" 서비스 클릭
3. "Deployments" 탭 클릭
4. 최신 배포 항목의 "..." 메뉴 → "Run Command"
5. 명령 실행: `python manage.py migrate`

## 대안: Railway CLI 문제 해결

Railway CLI가 제대로 작동하지 않는다면:

1. Railway CLI 재설치:
   ```powershell
   npm uninstall -g @railway/cli
   npm i -g @railway/cli
   ```

2. Railway CLI 버전 확인:
   ```powershell
   railway --version
   ```

3. Railway CLI 로그아웃 후 재로그인:
   ```powershell
   railway logout
   railway login
   ```

## 임시 해결책 (권장하지 않음)

Railway 대시보드 접근이 정말 불가능한 경우, 시작 스크립트를 수정하여 마이그레이션을 자동으로 실행할 수 있지만, 이는 권장되지 않습니다 (성능 문제, 오류 처리 어려움 등).

**가장 좋은 방법은 Railway 대시보드 접근 문제를 해결하는 것입니다.**

