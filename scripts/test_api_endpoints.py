"""
API 엔드포인트 테스트 스크립트
"""
import requests
import json

BASE_URL = 'http://localhost:8000'

def test_api_endpoints():
    """API 엔드포인트 테스트"""
    print("=" * 60)
    print("API 엔드포인트 테스트")
    print("=" * 60)
    
    # 1. 인증 토큰 필요 (실제로는 로그인 후 토큰 사용)
    # 여기서는 인증 없이 테스트 (permission_classes 확인 필요)
    
    # 2. 통장 목록 조회
    print("\n1. 통장 목록 조회")
    print("-" * 60)
    try:
        response = requests.get(f'{BASE_URL}/api/accounts/category-accounts/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 성공: {len(data)}개 통장")
            if data:
                print(f"   첫 번째 통장: {data[0].get('name', 'N/A')}")
        elif response.status_code == 401:
            print("⚠️ 인증 필요 (정상)")
        else:
            print(f"❌ 실패: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인하세요.")
        print("   실행 명령: python manage.py runserver")
    except Exception as e:
        print(f"❌ 에러: {str(e)}")
    
    # 3. 절약 계산
    print("\n2. 절약 금액 계산")
    print("-" * 60)
    try:
        response = requests.get(f'{BASE_URL}/api/accounts/category-accounts/1/monthly-savings/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 성공: 절약 금액 ${data.get('savings', 0)}")
        elif response.status_code == 401:
            print("⚠️ 인증 필요 (정상)")
        elif response.status_code == 404:
            print("⚠️ 통장을 찾을 수 없습니다 (ID=1)")
        else:
            print(f"❌ 실패: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다.")
    except Exception as e:
        print(f"❌ 에러: {str(e)}")
    
    # 4. 투자 목록
    print("\n3. 투자 목록 조회")
    print("-" * 60)
    try:
        response = requests.get(f'{BASE_URL}/api/accounts/savings-rewards/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 성공: {len(data)}개 투자")
        elif response.status_code == 401:
            print("⚠️ 인증 필요 (정상)")
        else:
            print(f"❌ 실패: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다.")
    except Exception as e:
        print(f"❌ 에러: {str(e)}")
    
    # 5. 예치금 계좌
    print("\n4. 예치금 계좌 조회")
    print("-" * 60)
    try:
        response = requests.get(f'{BASE_URL}/api/accounts/deposit-account/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 성공: 계좌번호 {data.get('account_number', 'N/A')}")
            print(f"   잔액: ${data.get('balance', 0)}")
        elif response.status_code == 401:
            print("⚠️ 인증 필요 (정상)")
        else:
            print(f"❌ 실패: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다.")
    except Exception as e:
        print(f"❌ 에러: {str(e)}")
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)
    print("\n💡 인증이 필요한 엔드포인트는 로그인 후 토큰을 사용해야 합니다.")
    print("   프론트엔드에서 실제 사용자로 테스트하세요.")

if __name__ == '__main__':
    test_api_endpoints()

