# 데이터베이스 마이그레이션 실행 방법

## 문제
`relation "django_site" does not exist` 오류 → 데이터베이스 테이블이 생성되지 않음

## 해결 방법

### 방법 1: Railway 대시보드에서 직접 실행 (권장 - 즉시 실행)

1. Railway 대시보드 접속
2. 프로젝트 선택
3. 상단 메뉴에서 **"Deployments"** 탭 클릭
4. 최신 배포 항목의 **"..." (더보기)** 메뉴 클릭
5. **"Run Command"** 또는 **"Open Shell"** 선택
6. 다음 명령 실행:
   ```bash
   python manage.py migrate
   ```

또는:

- Railway 대시보드 → 프로젝트 → 상단 메뉴에서 **"Variables"** 옆의 **"Deployments"** 또는 **"Settings"** → **"Service"** 탭
- **"Run Command"** 또는 **"Console"** 버튼 찾기
- 명령 실행: `python manage.py migrate`

### 방법 2: Procfile release 프로세스 (자동화 - 다음 배포부터)

이미 `Procfile`에 `release` 프로세스를 추가했습니다:
```
release: python manage.py migrate --noinput
```

다음 배포부터는 자동으로 마이그레이션이 실행됩니다.

**현재 상태:**
- 코드가 push되면 Railway가 자동으로 재배포합니다
- 재배포 시 `release` 프로세스가 실행되어 마이그레이션이 자동으로 실행됩니다

## 확인

마이그레이션 실행 후:
- `/admin/` 접속 테스트 (로그인 페이지가 나타나야 함)
- `/api/accounts/` 같은 API 엔드포인트 테스트

