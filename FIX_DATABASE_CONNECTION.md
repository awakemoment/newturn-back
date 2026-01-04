# 데이터베이스 연결 문제 해결

## 문제
IPv6 직접 연결 오류: `connection to server at "db.uczmhthbebuptmkrvbdh.supabase.co" (2600:1f18:2e13:9d3b:5dfe:bc39:82e:ae5c), port 5432 failed: Network is unreachable`

## 해결 방법

### 1. Supabase에서 Session Pooler URI 확인

1. Supabase 대시보드 접속
2. 왼쪽 사이드바: **Settings** → **Database**
3. 또는 상단 **"Connect"** 버튼 클릭
4. "Connect to your project" 모달에서:
   - **"Source"** 드롭다운을 **"Connection Pooler"**로 변경
   - Session Pooler URI 복사

**URI 형식:**
```
postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres
```

**특징:**
- `postgres.xxxxx` (점 포함)
- 포트: `6543`
- 호스트: `pooler.supabase.com` 또는 `aws-0-...pooler.supabase.com`

### 2. Railway에서 DATABASE_URL 업데이트

1. Railway 대시보드 접속
2. 프로젝트 선택
3. **"Variables"** 탭 클릭
4. **`DATABASE_URL`** 환경변수 찾기
5. **"Edit"** 클릭
6. Session Pooler URI로 **전체 교체**
   - 기존: `postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres`
   - 새로: `postgresql://postgres.xxxxx:[PASSWORD]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres`
7. **"Save"** 클릭

### 3. Railway 재배포

환경변수 업데이트 후 Railway가 자동으로 재배포합니다. 또는:
- **"Deployments"** 탭에서 최신 배포 확인
- 재배포가 자동으로 시작됩니다

### 4. 확인

배포 완료 후:
- `/api/accounts/` 같은 API 엔드포인트 테스트
- 로그에서 데이터베이스 연결 오류가 사라졌는지 확인

