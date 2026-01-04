# Railway에서 마이그레이션 실행 (해결 방법)

## 문제
`railway run python manage.py migrate`를 실행했는데 로컬 환경(LOCAL)에서 실행되고 "No migrations to apply"가 나옴.

## 원인
Railway CLI가 환경변수를 제대로 전달하지 않아 Django가 로컬 설정을 사용하고 있음.

## 해결 방법

### 방법 1: 환경변수 명시적으로 지정 (권장)

터미널에서 실행:

```powershell
railway run python manage.py migrate --settings=config.settings.production
```

또는:

```powershell
railway run bash -c "export DJANGO_SETTINGS_MODULE=config.settings.production && python manage.py migrate"
```

### 방법 2: Railway 환경변수 확인 및 설정

1. Railway 환경변수 확인:
   ```powershell
   railway variables
   ```

2. `DJANGO_SETTINGS_MODULE`이 `config.settings.production`으로 설정되어 있는지 확인

3. 없으면 추가:
   ```powershell
   railway variables set DJANGO_SETTINGS_MODULE=config.settings.production
   ```

4. 다시 마이그레이션 실행:
   ```powershell
   railway run python manage.py migrate
   ```

### 방법 3: Railway 대시보드 사용 (가능한 경우)

Railway 웹사이트 접속이 가능하면:
1. Railway 대시보드 → 프로젝트 → 서비스
2. "Deployments" 탭 → "Run Command"
3. 명령 실행: `python manage.py migrate --settings=config.settings.production`

## 확인

마이그레이션 실행 후:
- `/admin/` 접속 → 로그인 페이지 표시
- `/swagger/` 접속 → API 문서 표시
- `/api/accounts/` 접속 → API 응답 확인

