"""
시뮬레이션 모드 구현

Alpaca/Plaid API 인터페이스를 따르지만, 실제 API 호출 없이 DB 기반으로 동작
"""
import uuid
from decimal import Decimal
from typing import Optional, List, Dict
from datetime import date, datetime, timedelta
from django.utils import timezone
from django.db import transaction

from apps.stocks.models import Stock, StockPrice
from apps.accounts.models import DepositAccount, SavingsReward
from .interfaces import BrokerAPIInterface, BankAPIInterface


class SimulationBrokerAPI(BrokerAPIInterface):
    """시뮬레이션 주식 매매 API (Alpaca 호환 인터페이스)"""
    
    def __init__(self, deposit_account: Optional[DepositAccount] = None):
        """
        Args:
            deposit_account: 예치금 계좌 (None이면 전역 시뮬레이션)
        """
        self.deposit_account = deposit_account
        self._orders = {}  # 주문 저장소 (실제로는 DB에 저장)
        self._positions = {}  # 포지션 저장소 (실제로는 DB에서 조회)
    
    def get_current_price(self, symbol: str) -> Decimal:
        """현재가 조회 (StockPrice 테이블 사용)"""
        try:
            stock = Stock.objects.get(stock_code=symbol.upper())
            latest_price = StockPrice.objects.filter(
                stock=stock
            ).order_by('-date').first()
            
            if not latest_price:
                raise ValueError(f"주가 데이터를 찾을 수 없습니다: {symbol}")
            
            return Decimal(str(latest_price.close_price))
        except Stock.DoesNotExist:
            raise ValueError(f"종목을 찾을 수 없습니다: {symbol}")
    
    def buy_stock(
        self,
        symbol: str,
        quantity: float,  # 시뮬레이션은 소수점 허용
        order_type: str = 'market',
        limit_price: Optional[Decimal] = None
    ) -> Dict:
        """주식 매수 (시뮬레이션)"""
        quantity_decimal = Decimal(str(quantity))
        if quantity_decimal <= 0:
            raise ValueError("매수 주수는 0보다 커야 합니다.")
        
        # 현재가 조회
        current_price = self.get_current_price(symbol)
        execution_price = limit_price if order_type == 'limit' and limit_price else current_price
        
        # 예치금 확인 및 차감 (시뮬레이션에서는 선택적)
        # deposit_account가 있고 잔액이 충분하면 차감, 없거나 부족하면 가상 잔액 사용
        total_cost = execution_price * quantity_decimal
        if self.deposit_account and self.deposit_account.balance >= total_cost:
            # 예치금 계좌가 있고 잔액이 충분하면 차감
            self.deposit_account.balance -= total_cost
            self.deposit_account.save()
        # deposit_account가 없거나 잔액이 부족하면 시뮬레이션 가상 잔액 사용 (체크 없이 진행)
        
        # 주문 생성
        order_id = str(uuid.uuid4())
        filled_qty = quantity_decimal
        order = {
            'order_id': order_id,
            'status': 'filled',  # 시뮬레이션은 즉시 체결
            'filled_qty': filled_qty,
            'filled_avg_price': execution_price,
            'commission': Decimal('0'),
            'symbol': symbol.upper(),
            'side': 'buy',
            'order_type': order_type,
            'created_at': timezone.now(),
        }
        
        self._orders[order_id] = order
        
        # 포지션 업데이트 (실제로는 DB에 저장)
        if symbol.upper() not in self._positions:
            self._positions[symbol.upper()] = {
                'symbol': symbol.upper(),
                'qty': Decimal('0'),
                'avg_entry_price': Decimal('0'),
                'total_cost': Decimal('0'),
            }
        
        pos = self._positions[symbol.upper()]
        total_cost = pos['total_cost'] + (execution_price * filled_qty)
        total_qty = pos['qty'] + filled_qty
        pos['qty'] = total_qty
        pos['avg_entry_price'] = total_cost / total_qty if total_qty > 0 else Decimal('0')
        pos['total_cost'] = total_cost
        
        return order
    
    def sell_stock(
        self,
        symbol: str,
        quantity: float,  # 시뮬레이션은 소수점 허용
        order_type: str = 'market',
        limit_price: Optional[Decimal] = None
    ) -> Dict:
        """주식 매도 (시뮬레이션)"""
        quantity_decimal = Decimal(str(quantity))
        if quantity_decimal <= 0:
            raise ValueError("매도 주수는 0보다 커야 합니다.")
        
        # 포지션 확인
        if symbol.upper() not in self._positions:
            raise ValueError(f"보유하지 않은 종목입니다: {symbol}")
        
        pos = self._positions[symbol.upper()]
        if pos['qty'] < quantity_decimal:
            raise ValueError(f"보유 주수({pos['qty']})보다 매도 주수({quantity_decimal})가 많습니다.")
        
        # 현재가 조회
        current_price = self.get_current_price(symbol)
        execution_price = limit_price if order_type == 'limit' and limit_price else current_price
        
        # 주문 생성
        order_id = str(uuid.uuid4())
        sale_proceeds = execution_price * quantity_decimal
        commission = Decimal('0')
        net_proceeds = sale_proceeds - commission
        
        order = {
            'order_id': order_id,
            'status': 'filled',
            'filled_qty': quantity_decimal,
            'filled_avg_price': execution_price,
            'commission': commission,
            'symbol': symbol.upper(),
            'side': 'sell',
            'order_type': order_type,
            'created_at': timezone.now(),
        }
        
        self._orders[order_id] = order
        
        # 예치금 입금 (트랜잭션 내에서)
        if self.deposit_account:
            from django.db import transaction
            with transaction.atomic():
                self.deposit_account.balance += net_proceeds
                self.deposit_account.save()
        
        # 포지션 업데이트
        pos['qty'] -= quantity_decimal
        if pos['qty'] <= Decimal('0'):
            pos['avg_entry_price'] = Decimal('0')
            pos['total_cost'] = Decimal('0')
            pos['qty'] = Decimal('0')
        else:
            pos['total_cost'] = pos['avg_entry_price'] * pos['qty']
        
        return order
    
    def get_account_balance(self) -> Decimal:
        """계좌 잔액 조회"""
        if self.deposit_account:
            return self.deposit_account.balance
        return Decimal('100000')  # 기본 시뮬레이션 잔액
    
    def get_positions(self) -> List[Dict]:
        """보유 포지션 조회"""
        positions = []
        
        for symbol, pos in self._positions.items():
            if pos['qty'] <= 0:
                continue
            
            current_price = self.get_current_price(symbol)
            market_value = current_price * pos['qty']
            unrealized_pl = market_value - pos['total_cost']
            unrealized_plpc = (unrealized_pl / pos['total_cost'] * 100) if pos['total_cost'] > 0 else Decimal('0')
            
            positions.append({
                'symbol': symbol,
                'qty': pos['qty'],
                'avg_entry_price': pos['avg_entry_price'],
                'current_price': current_price,
                'market_value': market_value,
                'unrealized_pl': unrealized_pl,
                'unrealized_plpc': unrealized_plpc,
                'side': 'long',
            })
        
        return positions
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """특정 종목 보유 포지션 조회"""
        symbol_upper = symbol.upper()
        
        if symbol_upper not in self._positions:
            return None
        
        pos = self._positions[symbol_upper]
        if pos['qty'] <= 0:
            return None
        
        current_price = self.get_current_price(symbol_upper)
        market_value = current_price * pos['qty']
        unrealized_pl = market_value - pos['total_cost']
        unrealized_plpc = (unrealized_pl / pos['total_cost'] * 100) if pos['total_cost'] > 0 else Decimal('0')
        
        return {
            'symbol': symbol_upper,
            'qty': pos['qty'],
            'avg_entry_price': pos['avg_entry_price'],
            'current_price': current_price,
            'market_value': market_value,
            'unrealized_pl': unrealized_pl,
            'unrealized_plpc': unrealized_plpc,
        }
    
    def get_account(self) -> Dict:
        """계좌 정보 조회"""
        cash = self.get_account_balance()
        positions = self.get_positions()
        portfolio_value = cash + sum(p['market_value'] for p in positions)
        
        return {
            'account_number': self.deposit_account.account_number if self.deposit_account else 'SIM-001',
            'cash': cash,
            'portfolio_value': portfolio_value,
            'buying_power': cash,  # 시뮬레이션에서는 현금 = 구매력
            'equity': portfolio_value,
            'day_trading_buying_power': cash,
            'pattern_day_trader': False,
            'trading_blocked': False,
            'account_blocked': False,
            'status': 'ACTIVE',
        }
    
    def get_orders(self, status: str = 'all', limit: int = 50) -> List[Dict]:
        """주문 내역 조회"""
        orders = list(self._orders.values())
        
        if status == 'open':
            orders = [o for o in orders if o['status'] in ['new', 'partially_filled']]
        elif status == 'closed':
            orders = [o for o in orders if o['status'] in ['filled', 'canceled']]
        
        # 최신순 정렬
        orders.sort(key=lambda x: x['created_at'], reverse=True)
        
        return orders[:limit]
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """특정 주문 조회"""
        return self._orders.get(order_id)
    
    def cancel_order(self, order_id: str) -> bool:
        """주문 취소"""
        if order_id not in self._orders:
            return False
        
        order = self._orders[order_id]
        if order['status'] in ['filled', 'canceled']:
            return False
        
        order['status'] = 'canceled'
        return True


class SimulationBankAPI(BankAPIInterface):
    """시뮬레이션 은행 계좌 API (Plaid 호환 인터페이스)"""
    
    def __init__(self):
        self._link_tokens = {}  # Link Token 저장소
        self._access_tokens = {}  # Access Token 저장소
        self._accounts = {}  # 계좌 저장소
        self._transactions = {}  # 거래 내역 저장소
    
    def create_link_token(self, user_id: str) -> str:
        """Link Token 생성 (시뮬레이션)"""
        link_token = f"link-simulation-{uuid.uuid4()}"
        self._link_tokens[link_token] = {
            'user_id': user_id,
            'created_at': timezone.now(),
        }
        return link_token
    
    def exchange_public_token(self, public_token: str) -> str:
        """Public Token을 Access Token으로 교환 (시뮬레이션)"""
        # 시뮬레이션에서는 public_token을 그대로 access_token으로 사용
        access_token = f"access-simulation-{uuid.uuid4()}"
        self._access_tokens[access_token] = {
            'public_token': public_token,
            'created_at': timezone.now(),
        }
        return access_token
    
    def get_accounts(self, access_token: str) -> List[Dict]:
        """연결된 계좌 목록 조회 (시뮬레이션) - Wells Fargo"""
        if access_token not in self._access_tokens:
            return []
        
        # 시뮬레이션 계좌 생성 (Wells Fargo) - 프론트엔드와 동일한 ID 사용
        if access_token not in self._accounts:
            # 프론트엔드에서 사용하는 계좌 ID와 동일하게 설정
            checking_id = "acc-wells-checking"
            savings_id = "acc-wells-savings"
            
            self._accounts[access_token] = [
                {
                    'account_id': checking_id,
                    'name': 'Wells Fargo Everyday Checking',
                    'type': 'depository',
                    'subtype': 'checking',
                    'balance': Decimal('5000.00'),  # Wells Fargo 시뮬레이션 잔액
                    'mask': '1234',
                    'institution_name': 'Wells Fargo',
                },
                {
                    'account_id': savings_id,
                    'name': 'Wells Fargo Way2Save Savings',
                    'type': 'depository',
                    'subtype': 'savings',
                    'balance': Decimal('10000.00'),
                    'mask': '5678',
                    'institution_name': 'Wells Fargo',
                }
            ]
        
        return self._accounts[access_token]
    
    def get_account_balance(self, access_token: str, account_id: str) -> Decimal:
        """특정 계좌 잔액 조회 (시뮬레이션)"""
        accounts = self.get_accounts(access_token)
        account = next((acc for acc in accounts if acc['account_id'] == account_id), None)
        
        if not account:
            raise ValueError(f"계좌를 찾을 수 없습니다: {account_id}")
        
        return account['balance']
    
    def get_transactions(self, access_token: str, start_date: date, end_date: date) -> List[Dict]:
        """거래 내역 조회 (시뮬레이션) - Wells Fargo 거래 내역"""
        if access_token not in self._transactions:
            # Wells Fargo 시뮬레이션 거래 내역 생성
            now = timezone.now()
            self._transactions[access_token] = [
                {
                    'transaction_id': f"txn-{uuid.uuid4()}",
                    'name': 'STARBUCKS STORE #12345',
                    'merchant_name': 'Starbucks',
                    'amount': Decimal('-5.50'),
                    'date': (now - timedelta(days=1)).date(),
                    'authorized_date': (now - timedelta(days=1)).date(),
                    'category': ['Food and Drink', 'Restaurants', 'Coffee Shops'],
                },
                {
                    'transaction_id': f"txn-{uuid.uuid4()}",
                    'name': 'DUNKIN DONUTS #9876',
                    'merchant_name': 'Dunkin Donuts',
                    'amount': Decimal('-3.25'),
                    'date': (now - timedelta(days=2)).date(),
                    'authorized_date': (now - timedelta(days=2)).date(),
                    'category': ['Food and Drink', 'Restaurants', 'Coffee Shops'],
                },
                {
                    'transaction_id': f"txn-{uuid.uuid4()}",
                    'name': 'WHOLE FOODS MARKET',
                    'merchant_name': 'Whole Foods Market',
                    'amount': Decimal('-45.67'),
                    'date': (now - timedelta(days=3)).date(),
                    'authorized_date': (now - timedelta(days=3)).date(),
                    'category': ['Food and Drink', 'Groceries'],
                },
                {
                    'transaction_id': f"txn-{uuid.uuid4()}",
                    'name': 'NETFLIX.COM',
                    'merchant_name': 'Netflix',
                    'amount': Decimal('-15.99'),
                    'date': (now - timedelta(days=5)).date(),
                    'authorized_date': (now - timedelta(days=5)).date(),
                    'category': ['Shops', 'Digital Purchase'],
                },
                {
                    'transaction_id': f"txn-{uuid.uuid4()}",
                    'name': 'DIRECT DEPOSIT PAYROLL',
                    'merchant_name': None,
                    'amount': Decimal('3000.00'),
                    'date': (now - timedelta(days=7)).date(),
                    'authorized_date': (now - timedelta(days=7)).date(),
                    'category': ['Transfer', 'Payroll'],
                },
            ]
        
        transactions = self._transactions[access_token]
        
        # 날짜 필터링
        filtered = [
            txn for txn in transactions
            if start_date <= txn['date'] <= end_date
        ]
        
        return filtered

