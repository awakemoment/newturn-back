"""
브로커 API 팩토리

설정에 따라 시뮬레이션 또는 실제 API 인스턴스 반환
환경변수로 쉽게 전환 가능
"""
import os
from django.conf import settings
from .interfaces import BrokerAPIInterface, BankAPIInterface
from .simulation import SimulationBrokerAPI, SimulationBankAPI


def get_broker_api(deposit_account=None, force_simulation: bool = None) -> BrokerAPIInterface:
    """
    주식 매매 API 인스턴스 반환
    
    Args:
        deposit_account: 예치금 계좌 (시뮬레이션 모드에서 사용)
        force_simulation: 강제로 시뮬레이션 사용 (None이면 환경변수 확인)
    
    Returns:
        BrokerAPIInterface 구현체
    """
    if force_simulation is None:
        use_simulation = os.getenv('USE_SIMULATION_BROKER', 'True').lower() == 'true'
    else:
        use_simulation = force_simulation
    
    if use_simulation:
        return SimulationBrokerAPI(deposit_account=deposit_account)
    else:
        # 실제 Alpaca API 사용
        from .alpaca_api import AlpacaBrokerAPI
        paper_mode = os.getenv('ALPACA_PAPER', 'True').lower() == 'true'
        return AlpacaBrokerAPI(paper=paper_mode)


def get_bank_api(force_simulation: bool = None) -> BankAPIInterface:
    """
    은행 계좌 API 인스턴스 반환
    
    Args:
        force_simulation: 강제로 시뮬레이션 사용 (None이면 환경변수 확인)
    
    Returns:
        BankAPIInterface 구현체
    """
    if force_simulation is None:
        use_simulation = os.getenv('USE_SIMULATION_BANK', 'True').lower() == 'true'
    else:
        use_simulation = force_simulation
    
    if use_simulation:
        return SimulationBankAPI()
    else:
        # 실제 Plaid API 사용
        from .plaid_api import PlaidBankAPI
        return PlaidBankAPI()

