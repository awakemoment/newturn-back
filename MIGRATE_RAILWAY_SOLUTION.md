# Railway 마이그레이션 실행 - 최종 해결 방법

## 문제 분석
- `railway run python manage.py migrate` 실행 시 로컬 환경(LOCAL)에서 실행됨
- Railway 환경변수는 올바르게 설정되어 있음 (`DJANGO_SETTINGS_MODULE=config.settings.production`)

## 해결 방법

### 방법 1: --settings 플래그 사용

터미널에서 실행:

```powershell
railway run python manage.py migrate --settings=config.settings.production
```

### 방법 2: Railway CLI 환경변수 확인

Railway CLI가 환경변수를 제대로 전달하는지 확인:

```powershell
railway run env | findstr DJANGO_SETTINGS_MODULE
```

그 다음 마이그레이션 실행:

```powershell
railway run python manage.py migrate --settings=config.settings.production
```

## 확인

마이그레이션 실행 후 Railway 로그 확인:
- Railway 대시보드 → Deployments → 로그 확인
- 또는: `railway logs`

성공하면:
- `/admin/` 접속 → 로그인 페이지 표시
- `/swagger/` 접속 → API 문서 표시
- `/api/accounts/` 접속 → API 응답 확인

