"""
Polygon.io를 사용한 주가 데이터 수집

무료 플랜: 5 calls/min
"""
import os
import sys
import django
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .env 파일 로드
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.stocks.models import Stock, StockPrice
from django.conf import settings

# Polygon.io API 키
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY', '')

if not POLYGON_API_KEY:
    print("❌ POLYGON_API_KEY 환경 변수가 설정되지 않았습니다!")
    print("   .env.local 파일에 추가하세요:")
    print("   POLYGON_API_KEY=your_api_key_here")
    sys.exit(1)


def get_previous_close(ticker):
    """
    전일 종가 가져오기
    
    API: https://api.polygon.io/v2/aggs/ticker/{ticker}/prev
    """
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev"
    params = {'apiKey': POLYGON_API_KEY}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'OK' and data.get('results'):
            result = data['results'][0]
            return {
                'date': datetime.fromtimestamp(result['t'] / 1000).date(),
                'open': result['o'],
                'high': result['h'],
                'low': result['l'],
                'close': result['c'],
                'volume': result['v'],
            }
        else:
            return None
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print("   ⚠️ Rate Limit 초과! 1분 대기...")
            time.sleep(60)
            return get_previous_close(ticker)  # 재시도
        else:
            return None
    except Exception as e:
        print(f"   ❌ API 에러: {e}")
        return None


def collect_prices_batch(stocks, batch_size=5):
    """
    배치로 주가 수집 (Rate Limit 고려)
    
    무료 플랜: 5 calls/min → 12초마다 1개
    """
    print(f"\n📊 주가 수집 시작 (배치 크기: {batch_size})")
    print(f"⏱️  예상 소요 시간: ~{len(stocks) * 12 // 60}분")
    print()
    
    success_count = 0
    fail_count = 0
    
    for i, stock in enumerate(stocks, 1):
        print(f"[{i}/{len(stocks)}] {stock.stock_code} - {stock.stock_name[:30]}")
        
        # 전일 종가 가져오기
        price_data = get_previous_close(stock.stock_code)
        
        if price_data:
            # DB 저장
            try:
                StockPrice.objects.update_or_create(
                    stock=stock,
                    date=price_data['date'],
                    defaults={
                        'open_price': price_data['open'],
                        'high_price': price_data['high'],
                        'low_price': price_data['low'],
                        'close_price': price_data['close'],
                        'volume': price_data['volume'],
                    }
                )
                print(f"   ✅ ${price_data['close']:.2f} (Vol: {price_data['volume']:,})")
                success_count += 1
            except Exception as e:
                print(f"   ❌ 저장 실패: {e}")
                fail_count += 1
        else:
            print(f"   ⚠️ 데이터 없음")
            fail_count += 1
        
        # Rate Limit 준수: 12초 대기 (5 calls/min)
        if i < len(stocks):
            time.sleep(12)
        
        # 진행 상황
        if i % 10 == 0:
            print(f"\n📊 진행률: {i}/{len(stocks)} ({i/len(stocks)*100:.1f}%)")
            print(f"   성공: {success_count}개 | 실패: {fail_count}개\n")
    
    return success_count, fail_count


def main():
    print("\n" + "="*70)
    print("📈 Polygon.io 주가 수집")
    print("="*70)
    
    # 수집 대상: 메이트 점수가 있는 종목만 (우선)
    from apps.analysis.models import MateAnalysis
    
    stocks_with_mates = MateAnalysis.objects.values_list('stock_id', flat=True).distinct()
    stocks = Stock.objects.filter(
        id__in=stocks_with_mates,
        country='us',
        is_active=True
    )
    
    total = stocks.count()
    print(f"\n📌 수집 대상: {total:,}개 종목 (메이트 분석 완료 종목)")
    print(f"⏱️  예상 소요 시간: ~{total * 12 // 60}분 (5 calls/min)")
    
    # 사용자 확인
    response = input("\n계속하시겠습니까? (y/n): ")
    if response.lower() != 'y':
        print("취소되었습니다.")
        return
    
    # 수집 시작
    success, fail = collect_prices_batch(list(stocks))
    
    # 최종 결과
    print("\n" + "="*70)
    print("🎉 주가 수집 완료!")
    print("="*70)
    print(f"✅ 성공: {success:,}개")
    print(f"❌ 실패: {fail:,}개")
    print(f"📊 성공률: {success/(success+fail)*100:.1f}%")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()

