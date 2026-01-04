# 🔧 Supabase 데이터베이스 연결 오류 해결

**오류**: `Network is unreachable` (IPv6 연결 실패)

---

## 🚨 **문제 원인**

Railway에서 Supabase로 IPv6 주소로 연결을 시도하는데, Railway가 IPv6를 지원하지 않거나 Supabase의 Direct Connection이 IPv4를 지원하지 않아 발생하는 오류입니다.

---

## ✅ **해결 방법: Connection Pooler 사용**

Supabase의 **Session Pooler**를 사용하면 IPv4 연결이 가능합니다.

### **1. Supabase에서 Connection Pooler URI 확인**

1. Supabase 대시보드 → **Project Settings** → **Database**
2. **"Connection string"** 섹션 찾기
3. **"Connection pooling"** 섹션 클릭
4. **"Session mode"** URI 복사

**예시 형식:**
```
postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres
```

**Direct Connection (현재 사용 중 - 오류 발생):**
```
postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

**Session Pooler (IPv4 호환 - 사용해야 함):**
```
postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres
```

---

## 🔧 **Railway 환경변수 수정**

### **Railway 대시보드에서:**

1. Railway 대시보드 → "web" 서비스 → **"Variables"** 탭
2. **DATABASE_URL** 환경변수 찾기
3. **"Edit"** 클릭
4. **Session Pooler URI**로 변경
5. **"Save"** 클릭

### **변경 전 (Direct Connection):**
```
postgresql://postgres:@AB4832299cd@db.uczmhthbebuptmkrvbdh.supabase.co:5432/postgres
```

### **변경 후 (Session Pooler):**
```
postgresql://postgres.uczmhthbebuptmkrvbdh:@AB4832299cd@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres
```

**⚠️ 주의**: 
- `postgres.xxxxx` 형식 (점 포함)
- 포트: `6543` (5432가 아님)
- 호스트: `pooler.supabase.com` (db.xxxxx가 아님)

---

## 📋 **Session Pooler URI 찾는 방법**

1. Supabase 대시보드 접속
2. **Project Settings** → **Database**
3. **"Connection string"** 섹션 찾기
4. 드롭다운에서 **"Connection pooling"** 선택
5. **"Session mode"** URI 복사

또는 "Connect to your project" 모달에서:
1. **"Connection String"** 탭
2. **"Source"** 드롭다운에서 **"Connection Pooler"** 선택
3. URI 복사

---

## ✅ **수정 후 확인**

1. Railway 환경변수 업데이트 완료
2. Railway가 자동으로 재배포 (또는 수동 재배포)
3. 배포 로그에서 데이터베이스 연결 성공 확인
4. API 테스트:
   ```bash
   curl https://web-production-faaf3.up.railway.app/api/stocks/
   ```

---

## 🔍 **추가 참고사항**

### **Session Pooler vs Direct Connection**

- **Session Pooler**: IPv4 호환, 연결 풀링, Railway 권장 ✅
- **Direct Connection**: IPv6만, 연결 풀링 없음, Railway에서 문제 발생 ❌

### **Staticfiles 경고**

```
UserWarning: No directory at: /app/staticfiles/
```

이 경고는 `collectstatic`을 실행하면 해결됩니다:

```bash
railway run python manage.py collectstatic --noinput
```

---

**마지막 업데이트**: 2025.01.14

