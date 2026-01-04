# Railway 마이그레이션 실행 - 대안 방법

## 문제
Railway 대시보드의 Deployments 탭에서 "Run Command" 옵션을 찾을 수 없음.

## 해결 방법

### 방법 1: Settings 탭 확인

1. "Settings" 탭 클릭
2. "Service" 섹션에서 "Run Command" 또는 "Console" 버튼 찾기
3. 또는 "Shell" 또는 "Terminal" 옵션 찾기

### 방법 2: Railway CLI 사용 (추천)

Railway CLI를 사용하여 원격으로 마이그레이션 실행:

```powershell
# 프로젝트 디렉토리에서
cd C:\projects\business\newturn-back

# Railway 환경변수로 마이그레이션 실행
railway run --service web python manage.py migrate
```

또는 환경변수를 명시적으로 지정:

```powershell
railway run --service web --env DJANGO_SETTINGS_MODULE=config.settings.production python manage.py migrate
```

### 방법 3: 마이그레이션 스크립트 생성 후 배포

임시로 마이그레이션을 실행하는 스크립트를 만들고, 이를 Railway에서 실행:

1. `scripts/run_migration.py` 파일 생성
2. GitHub에 push
3. Railway가 자동 배포
4. 스크립트 실행

하지만 이 방법은 복잡하고 권장하지 않습니다.

## 가장 간단한 방법

**Railway CLI를 사용하는 것이 가장 간단합니다:**

```powershell
cd C:\projects\business\newturn-back
railway run --service web python manage.py migrate
```

또는 Settings 탭을 확인해보세요.

