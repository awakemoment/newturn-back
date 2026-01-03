# Celery 설정 및 사용 가이드

**작성일**: 2025-01-13  
**목적**: 주가 업데이트 스케줄러 설정 및 사용 방법

---

## 📋 개요

Celery를 사용하여 주가 업데이트 작업을 자동으로 실행합니다.

**주요 기능:**
- 모든 투자 중인 SavingsReward의 주가 자동 업데이트
- 매일 오후 6시 (미국 시장 마감 후) 실행
- 단일 리워드 주가 업데이트 (수동 실행 가능)

---

## 🔧 설정

### 1. Redis 설치 (Celery 브로커)

**Windows:**
```bash
# Chocolatey 사용
choco install redis-64

# 또는 WSL 사용
wsl
sudo apt-get update
sudo apt-get install redis-server
sudo service redis-server start
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

### 2. 환경변수 설정

`.env` 파일에 Redis 설정 추가 (선택사항):
```bash
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

기본값이 `redis://localhost:6379/0`이므로 생략 가능합니다.

---

## 🚀 실행 방법

### 1. Celery Worker 실행

터미널 1:
```bash
cd C:\projects\business\newturn-back
celery -A newturn worker -l info
```

### 2. Celery Beat 실행 (스케줄러)

터미널 2:
```bash
cd C:\projects\business\newturn-back
celery -A newturn beat -l info
```

### 3. Django 개발 서버 실행

터미널 3:
```bash
cd C:\projects\business\newturn-back
python manage.py runserver
```

---

## 📝 작업 설명

### `update_reward_prices`

**설명**: 모든 투자 중인 SavingsReward의 주가를 업데이트

**실행 시간**: 매일 오후 6시 (미국 시장 마감 후)

**작업 내용:**
1. `status='invested'`인 모든 SavingsReward 조회
2. 각 리워드의 종목 코드로 현재가 조회
3. `current_price` 업데이트
4. `update_current_value()` 호출하여 가치 재계산

**수동 실행:**
```python
# Django shell에서
from apps.accounts.tasks import update_reward_prices
result = update_reward_prices.delay()
print(result.get())
```

---

### `update_single_reward_price`

**설명**: 단일 SavingsReward의 주가 업데이트

**파라미터:**
- `reward_id`: SavingsReward ID

**사용 예:**
```python
# Django shell에서
from apps.accounts.tasks import update_single_reward_price
result = update_single_reward_price.delay(reward_id=1)
print(result.get())
```

---

## 🧪 테스트

### 1. 작업 테스트

```bash
# Django shell 실행
python manage.py shell

# 작업 직접 실행 (비동기 X)
from apps.accounts.tasks import update_reward_prices
result = update_reward_prices()
print(result)
```

### 2. Celery Worker 테스트

```bash
# Worker 실행 후
celery -A newturn worker -l info

# 다른 터미널에서
python manage.py shell
from apps.accounts.tasks import update_reward_prices
result = update_reward_prices.delay()  # 비동기 실행
print(result.id)  # Task ID
```

---

## ⚙️ 스케줄 조정

스케줄을 변경하려면 `config/settings/base.py`의 `CELERY_BEAT_SCHEDULE`을 수정하세요:

```python
CELERY_BEAT_SCHEDULE = {
    'update-reward-prices-daily': {
        'task': 'accounts.update_reward_prices',
        'schedule': crontab(hour=18, minute=0),  # 매일 오후 6시
        # 또는
        # 'schedule': crontab(hour='*/6'),  # 6시간마다
        # 'schedule': crontab(minute='*/30'),  # 30분마다
        'options': {'timezone': TIME_ZONE},
    },
}
```

**crontab 예시:**
- `crontab(hour=18, minute=0)` - 매일 오후 6시
- `crontab(hour='*/6')` - 6시간마다
- `crontab(minute='*/30')` - 30분마다
- `crontab(hour=9, minute=0, day_of_week='mon-fri')` - 평일 오전 9시

---

## 🐛 문제 해결

### Redis 연결 실패

**에러**: `Error 111 connecting to localhost:6379. Connection refused.`

**해결:**
1. Redis가 실행 중인지 확인:
   ```bash
   redis-cli ping
   # 응답: PONG
   ```

2. Redis 시작:
   ```bash
   redis-server
   ```

### 작업이 실행되지 않음

**확인사항:**
1. Celery Worker가 실행 중인지 확인
2. Celery Beat가 실행 중인지 확인
3. 작업 로그 확인 (`-l info` 또는 `-l debug`)

### 주가 조회 실패

**에러**: `Alpaca API 키가 설정되지 않았습니다.`

**해결:**
- 시뮬레이션 모드 사용: `.env`에 `USE_SIMULATION_BROKER=True` 설정
- 또는 Alpaca API 키 설정 (실제 API 사용 시)

---

## 📊 모니터링

### 작업 상태 확인

```bash
# Celery Flower (선택사항)
pip install flower
celery -A newturn flower

# 브라우저에서 http://localhost:5555 접속
```

### 로그 확인

작업 실행 로그는 콘솔 및 `newturn.log` 파일에 기록됩니다:

```
[INFO] 2025-01-13 18:00:00,123 tasks ✅ AAPL 업데이트 완료: $150.25 (리워드 ID: 1)
[INFO] 2025-01-13 18:00:00,456 tasks 주가 업데이트 완료: 5개 성공, 0개 실패
```

---

## 🎯 다음 단계

1. ✅ Celery 설정 완료
2. ✅ 주가 업데이트 작업 구현 완료
3. ⏳ 프로덕션 환경 배포 시 Celery 서비스 설정
4. ⏳ 모니터링 도구 (Flower) 설정

---

**작성일**: 2025-01-13  
**작성자**: AI Assistant

