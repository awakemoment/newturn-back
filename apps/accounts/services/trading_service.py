"""
투자 서비스 (브로커 API 추상화 사용)

시뮬레이션/실제 API를 동일한 방식으로 사용
"""
from decimal import Decimal
from django.utils import timezone
from apps.broker.factory import get_broker_api
from apps.accounts.models import DepositAccount, SavingsReward
from apps.stocks.models import Stock


class TradingService:
    """투자 서비스 (브로커 API 추상화)"""
    
    def __init__(self, deposit_account: DepositAccount = None):
        """
        Args:
            deposit_account: 예치금 계좌
        """
        self.deposit_account = deposit_account
        self.broker = get_broker_api(deposit_account=deposit_account)
    
    def execute_investment(self, reward: SavingsReward) -> SavingsReward:
        """
        실제 주식 매수 실행 (예치금에서 차감)
        
        Args:
            reward: SavingsReward 객체
        
        Returns:
            업데이트된 SavingsReward
        """
        # 1. 예치금 잔액 확인 (실제 모드에서만)
        # 시뮬레이션 모드: SimulationBrokerAPI가 자체적으로 예치금 관리
        if not self._is_simulation() and self.deposit_account and self.deposit_account.balance < reward.savings_amount:
            raise ValueError("예치금 잔액이 부족합니다.")
        
        # 2. 현재가 조회
        symbol = reward.stock.stock_code
        current_price = self.broker.get_current_price(symbol)
        
        # 3. 매수 가능 주수 계산
        # 시뮬레이션 모드: 소수점 주수 허용
        # 실제 모드: 정수 주수만 가능
        if self._is_simulation():
            shares = reward.savings_amount / current_price
            if shares < Decimal('0.0001'):  # 최소 0.0001주
                raise ValueError("투자 금액이 너무 적습니다.")
        else:
            shares = int(reward.savings_amount / current_price)
            if shares < 1:
                raise ValueError("최소 1주 이상 매수해야 합니다.")
            shares = Decimal(str(shares))
        
        # 4. 실제 매수 주문 (브로커 API)
        # 시뮬레이션 모드: 소수점 주수 허용
        # 실제 모드: 정수 주수만 가능
        if self._is_simulation():
            result = self.broker.buy_stock(
                symbol=symbol,
                quantity=float(shares),  # 시뮬레이션은 float 허용
                order_type='market'
            )
        else:
            result = self.broker.buy_stock(
                symbol=symbol,
                quantity=int(shares),  # 실제 모드는 정수만
                order_type='market'
            )
        
        # 5. 실제 매수 가격으로 재계산
        actual_cost = result['filled_avg_price'] * result['filled_qty']
        commission = result['commission']
        
        # 6. 예치금 차감 (시뮬레이션 모드에서는 이미 차감됨)
        if self.deposit_account:
            # 시뮬레이션 모드에서는 이미 차감되었으므로 확인만
            # 실제 모드에서는 여기서 차감
            if not self._is_simulation():
                self.deposit_account.balance -= actual_cost + commission
                self.deposit_account.save()
        
        # 7. 리워드 업데이트
        reward.purchase_price = result['filled_avg_price']
        reward.shares = result['filled_qty']
        reward.current_price = result['filled_avg_price']  # 초기 현재가 = 매수 가격
        reward.status = 'invested'
        reward.update_current_value()  # 수익/손실 계산
        reward.save()
        
        return reward
    
    def execute_sale(self, reward: SavingsReward) -> tuple:
        """
        실제 주식 매도 실행 (예치금에 입금)
        주의: 손실 상태에서도 매도 가능 (Marshmallow Experiment는 가이드라인)
        
        Args:
            reward: SavingsReward 객체
        
        Returns:
            (업데이트된 SavingsReward, 순수익)
        """
        if not reward.can_sell:
            raise ValueError("매도할 수 없는 상태입니다.")
        
        # 1. 현재가 조회
        symbol = reward.stock.stock_code
        
        # 2. 실제 매도 주문 (브로커 API)
        # 시뮬레이션 모드: 소수점 주수 허용
        # 실제 모드: 정수 주수만 가능
        if self._is_simulation():
            result = self.broker.sell_stock(
                symbol=symbol,
                quantity=float(reward.shares),  # 시뮬레이션은 float 허용
                order_type='market'
            )
        else:
            result = self.broker.sell_stock(
                symbol=symbol,
                quantity=int(reward.shares),  # 실제 모드는 정수만
                order_type='market'
            )
        
        # 3. 매도 금액 계산
        sale_proceeds = result['filled_avg_price'] * result['filled_qty']
        commission = result['commission']
        net_proceeds = sale_proceeds - commission
        
        # 4. 예치금 입금
        # 시뮬레이션 모드: SimulationBrokerAPI에서 이미 입금됨
        # 실제 모드: 여기서 입금
        if self.deposit_account and not self._is_simulation():
            from django.db import transaction
            with transaction.atomic():
                self.deposit_account.balance += net_proceeds
                self.deposit_account.save()
        
        # 5. 리워드 업데이트
        reward.sell_price = result['filled_avg_price']
        reward.sell_date = timezone.now()
        reward.commission = commission
        reward.net_proceeds = net_proceeds
        reward.status = 'sold'
        reward.save()
        
        # 6. 카테고리 계좌에 리워드 반영
        reward.account.realized_reward += net_proceeds
        reward.account.pending_reward -= reward.savings_amount
        reward.account.save()
        
        return reward, net_proceeds
    
    def sync_positions(self):
        """브로커 계좌의 실제 포지션과 DB 동기화"""
        # DB의 모든 투자 중인 리워드 업데이트
        if self.deposit_account:
            rewards = SavingsReward.objects.filter(
                account__user=self.deposit_account.user,
                status='invested'
            )
            
            for reward in rewards:
                try:
                    # 현재가 조회
                    current_price = self.broker.get_current_price(reward.stock.stock_code)
                    reward.current_price = current_price
                    reward.update_current_value()
                except Exception as e:
                    print(f"주가 업데이트 실패: {reward.stock.stock_code} - {str(e)}")
                    continue
    
    def _is_simulation(self) -> bool:
        """시뮬레이션 모드인지 확인"""
        import os
        return os.getenv('USE_SIMULATION_BROKER', 'True').lower() == 'true'

