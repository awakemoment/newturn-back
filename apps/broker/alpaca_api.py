"""
실제 Alpaca API 구현

BrokerAPIInterface를 구현하여 시뮬레이션과 동일한 인터페이스 제공
"""
import os
from decimal import Decimal
from typing import Optional, List, Dict
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

from .interfaces import BrokerAPIInterface


class AlpacaBrokerAPI(BrokerAPIInterface):
    """실제 Alpaca API 구현 (BrokerAPIInterface)"""
    
    def __init__(self, api_key: str = None, secret_key: str = None, paper: bool = True):
        """
        Alpaca API 초기화
        
        Args:
            api_key: Alpaca API Key (환경변수에서 가져옴)
            secret_key: Alpaca Secret Key (환경변수에서 가져옴)
            paper: Paper Trading 모드 (True) 또는 Live Trading (False)
        """
        self.api_key = api_key or os.getenv('ALPACA_API_KEY')
        self.secret_key = secret_key or os.getenv('ALPACA_SECRET_KEY')
        self.paper = paper if paper is not None else os.getenv('ALPACA_PAPER', 'True') == 'True'
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API 키가 설정되지 않았습니다.")
        
        # Trading Client (매수/매도)
        self.trading_client = TradingClient(
            api_key=self.api_key,
            secret_key=self.secret_key,
            paper=self.paper
        )
        
        # Data Client (주가 조회)
        self.data_client = StockHistoricalDataClient(
            api_key=self.api_key,
            secret_key=self.secret_key
        )
    
    def get_current_price(self, symbol: str) -> Decimal:
        """현재가 조회"""
        try:
            request = StockLatestQuoteRequest(symbol_or_symbols=[symbol.upper()])
            latest_quote = self.data_client.get_stock_latest_quote(request)
            
            if symbol.upper() in latest_quote:
                quote = latest_quote[symbol.upper()]
                # Bid와 Ask의 중간가 사용
                bid = Decimal(str(quote.bid_price))
                ask = Decimal(str(quote.ask_price))
                return (bid + ask) / 2
            else:
                raise ValueError(f"주가 데이터를 찾을 수 없습니다: {symbol}")
        except Exception as e:
            raise ValueError(f"주가 조회 실패: {str(e)}")
    
    def buy_stock(
        self,
        symbol: str,
        quantity: int,
        order_type: str = 'market',
        limit_price: Optional[Decimal] = None
    ) -> Dict:
        """주식 매수"""
        try:
            if quantity <= 0:
                raise ValueError("매수 주수는 1주 이상이어야 합니다.")
            
            if order_type == 'market':
                order_request = MarketOrderRequest(
                    symbol=symbol.upper(),
                    qty=quantity,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                )
            else:
                # Limit order
                if not limit_price:
                    limit_price = self.get_current_price(symbol)
                order_request = LimitOrderRequest(
                    symbol=symbol.upper(),
                    qty=quantity,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY,
                    limit_price=float(limit_price)
                )
            
            order = self.trading_client.submit_order(order_request)
            
            return {
                'order_id': str(order.id),
                'status': order.status.value,
                'filled_qty': Decimal(str(order.filled_qty or 0)),
                'filled_avg_price': Decimal(str(order.filled_avg_price or 0)),
                'commission': Decimal('0'),  # Alpaca는 커미션 무료
                'symbol': symbol.upper(),
                'side': 'buy',
                'order_type': order_type,
            }
        except Exception as e:
            raise ValueError(f"매수 주문 실패: {str(e)}")
    
    def sell_stock(
        self,
        symbol: str,
        quantity: int,
        order_type: str = 'market',
        limit_price: Optional[Decimal] = None
    ) -> Dict:
        """주식 매도"""
        try:
            if quantity <= 0:
                raise ValueError("매도 주수는 1주 이상이어야 합니다.")
            
            if order_type == 'market':
                order_request = MarketOrderRequest(
                    symbol=symbol.upper(),
                    qty=quantity,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                )
            else:
                if not limit_price:
                    limit_price = self.get_current_price(symbol)
                order_request = LimitOrderRequest(
                    symbol=symbol.upper(),
                    qty=quantity,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY,
                    limit_price=float(limit_price)
                )
            
            order = self.trading_client.submit_order(order_request)
            
            return {
                'order_id': str(order.id),
                'status': order.status.value,
                'filled_qty': Decimal(str(order.filled_qty or 0)),
                'filled_avg_price': Decimal(str(order.filled_avg_price or 0)),
                'commission': Decimal('0'),
                'symbol': symbol.upper(),
                'side': 'sell',
                'order_type': order_type,
            }
        except Exception as e:
            raise ValueError(f"매도 주문 실패: {str(e)}")
    
    def get_account_balance(self) -> Decimal:
        """계좌 잔액 조회"""
        account = self.trading_client.get_account()
        return Decimal(str(account.cash))
    
    def get_positions(self) -> List[Dict]:
        """보유 포지션 조회"""
        positions = self.trading_client.get_all_positions()
        return [
            {
                'symbol': pos.symbol,
                'qty': Decimal(str(pos.qty)),
                'avg_entry_price': Decimal(str(pos.avg_entry_price)),
                'current_price': Decimal(str(pos.current_price)),
                'market_value': Decimal(str(pos.market_value)),
                'unrealized_pl': Decimal(str(pos.unrealized_pl)),
                'unrealized_plpc': Decimal(str(pos.unrealized_plpc)),
                'side': pos.side.value,
            }
            for pos in positions
        ]
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """특정 종목 보유 포지션 조회"""
        try:
            position = self.trading_client.get_open_position(symbol.upper())
            return {
                'symbol': position.symbol,
                'qty': Decimal(str(position.qty)),
                'avg_entry_price': Decimal(str(position.avg_entry_price)),
                'current_price': Decimal(str(position.current_price)),
                'market_value': Decimal(str(position.market_value)),
                'unrealized_pl': Decimal(str(position.unrealized_pl)),
                'unrealized_plpc': Decimal(str(position.unrealized_plpc)),
            }
        except Exception:
            return None
    
    def get_account(self) -> Dict:
        """계좌 정보 조회"""
        account = self.trading_client.get_account()
        return {
            'account_number': account.account_number,
            'cash': Decimal(str(account.cash)),
            'portfolio_value': Decimal(str(account.portfolio_value)),
            'buying_power': Decimal(str(account.buying_power)),
            'equity': Decimal(str(account.equity)),
            'day_trading_buying_power': Decimal(str(account.day_trading_buying_power)),
            'pattern_day_trader': account.pattern_day_trader,
            'trading_blocked': account.trading_blocked,
            'account_blocked': account.account_blocked,
            'status': account.status.value,
        }
    
    def get_orders(self, status: str = 'all', limit: int = 50) -> List[Dict]:
        """주문 내역 조회"""
        from alpaca.trading.enums import QueryOrderStatus
        
        status_map = {
            'all': QueryOrderStatus.ALL,
            'open': QueryOrderStatus.OPEN,
            'closed': QueryOrderStatus.CLOSED,
        }
        
        orders = self.trading_client.get_orders(
            status=status_map.get(status, QueryOrderStatus.ALL),
            limit=limit
        )
        
        return [
            {
                'order_id': str(order.id),
                'symbol': order.symbol,
                'qty': Decimal(str(order.qty)),
                'filled_qty': Decimal(str(order.filled_qty or 0)),
                'side': order.side.value,
                'order_type': order.order_type.value,
                'status': order.status.value,
                'limit_price': Decimal(str(order.limit_price)) if order.limit_price else None,
                'stop_price': Decimal(str(order.stop_price)) if order.stop_price else None,
                'filled_avg_price': Decimal(str(order.filled_avg_price)) if order.filled_avg_price else None,
                'submitted_at': order.submitted_at.isoformat() if order.submitted_at else None,
                'filled_at': order.filled_at.isoformat() if order.filled_at else None,
            }
            for order in orders
        ]
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """특정 주문 조회"""
        try:
            order = self.trading_client.get_order_by_id(order_id)
            return {
                'order_id': str(order.id),
                'symbol': order.symbol,
                'qty': Decimal(str(order.qty)),
                'filled_qty': Decimal(str(order.filled_qty or 0)),
                'side': order.side.value,
                'order_type': order.order_type.value,
                'status': order.status.value,
                'limit_price': Decimal(str(order.limit_price)) if order.limit_price else None,
                'filled_avg_price': Decimal(str(order.filled_avg_price)) if order.filled_avg_price else None,
            }
        except Exception:
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """주문 취소"""
        try:
            self.trading_client.cancel_order_by_id(order_id)
            return True
        except Exception:
            return False

