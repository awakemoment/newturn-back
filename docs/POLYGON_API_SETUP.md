# Polygon.io API 설정 가이드

## 1. API 키 발급

1. https://polygon.io/ 접속
2. "Get Your Free API Key" 클릭
3. 회원가입 (무료)
4. API 키 복사

## 2. 무료 플랜 제한

- **5 calls/min**
- **5 API Calls / Minute** (충분함)
- Delayed data (15분 지연)
- Historical data (과거 데이터)

## 3. 환경 변수 설정

`.env.local` 파일에 추가:

```bash
POLYGON_API_KEY=your_api_key_here
```

## 4. 사용 예시

```python
import requests

API_KEY = "your_api_key"
TICKER = "AAPL"

# 최신 가격
url = f"https://api.polygon.io/v2/aggs/ticker/{TICKER}/prev?apiKey={API_KEY}"
response = requests.get(url)
data = response.json()

print(f"Close: ${data['results'][0]['c']}")
```

## 5. 대안 (더 많은 호출 필요 시)

### IEX Cloud
- 무료: 50,000 calls/월
- https://iexcloud.io/

### Alpha Vantage
- 무료: 25 calls/day (너무 적음)
- https://www.alphavantage.co/

## 추천: Polygon.io로 시작 → 필요시 업그레이드

