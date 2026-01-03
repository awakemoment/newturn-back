# 🎯 실행할 커맨드

**지금 즉시 실행하세요!**

---

## 1️⃣ 백엔드 재시작

```bash
# 기존 서버 Ctrl+C로 중지

# 재시작
cd C:\projects\business\newturn-back
conda activate newturn_back
python manage.py runserver
```

**→ "Starting development server..." 메시지 확인!**

---

## 2️⃣ 프론트엔드 재시작

```bash
# 새 터미널

cd C:\projects\business\newturn-front
npm run dev
```

---

## 3️⃣ 테스트

### **브라우저:**
```
http://localhost:3000/
```

### **테스트 항목:**
1. ✅ 메인 페이지 로딩
2. ✅ 스크리닝 → 종목 선택
3. ✅ 종목 상세 → 10-K 인사이트 (사업보고서 느낌!)
4. ✅ 종목 상세 → Learn 섹션 (AAPL 콘텐츠 10개!)
5. ✅ 관심종목 추가
6. ✅ Footer 면책 조항 확인

---

## 4️⃣ Admin 확인 (선택)

```
http://localhost:8000/admin/content/curatedcontent/
```

**→ AAPL 콘텐츠 10개 + 큐레이터 노트 확인!**

---

## 🎉 **완료되면**

**"완료! 잘 작동해"** 라고 알려주세요!

그럼 다음 작업 계속하겠습니다:
- 법적 문구 일괄 수정
- 종목 비교 페이지 개선

