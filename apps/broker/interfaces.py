"""
브로커 API 인터페이스 정의

실제 API (Alpaca/Plaid)와 시뮬레이션 모드를 동일한 인터페이스로 사용할 수 있도록 추상화
"""
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional, List, Dict
from datetime import date, datetime


class BrokerAPIInterface(ABC):
    """주식 매매 API 인터페이스 (Alpaca 호환)"""
    
    @abstractmethod
    def get_current_price(self, symbol: str) -> Decimal:
        """현재가 조회"""
        pass
    
    @abstractmethod
    def buy_stock(self, symbol: str, quantity: int, order_type: str = 'market', limit_price: Optional[Decimal] = None) -> Dict:
        """
        주식 매수
        
        Returns:
            {
                'order_id': str,
                'status': str,
                'filled_qty': Decimal,
                'filled_avg_price': Decimal,
                'commission': Decimal
            }
        """
        pass
    
    @abstractmethod
    def sell_stock(self, symbol: str, quantity: int, order_type: str = 'market', limit_price: Optional[Decimal] = None) -> Dict:
        """주식 매도"""
        pass
    
    @abstractmethod
    def get_account_balance(self) -> Decimal:
        """계좌 잔액 조회"""
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Dict]:
        """보유 포지션 조회"""
        pass
    
    @abstractmethod
    def get_position(self, symbol: str) -> Optional[Dict]:
        """특정 종목 보유 포지션 조회"""
        pass
    
    @abstractmethod
    def get_account(self) -> Dict:
        """계좌 정보 조회"""
        pass
    
    @abstractmethod
    def get_orders(self, status: str = 'all', limit: int = 50) -> List[Dict]:
        """주문 내역 조회"""
        pass
    
    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Dict]:
        """특정 주문 조회"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """주문 취소"""
        pass


class BankAPIInterface(ABC):
    """은행 계좌 API 인터페이스 (Plaid 호환)"""
    
    @abstractmethod
    def create_link_token(self, user_id: str) -> str:
        """Link Token 생성"""
        pass
    
    @abstractmethod
    def exchange_public_token(self, public_token: str) -> str:
        """Public Token을 Access Token으로 교환"""
        pass
    
    @abstractmethod
    def get_accounts(self, access_token: str) -> List[Dict]:
        """연결된 계좌 목록 조회"""
        pass
    
    @abstractmethod
    def get_account_balance(self, access_token: str, account_id: str) -> Decimal:
        """특정 계좌 잔액 조회"""
        pass
    
    @abstractmethod
    def get_transactions(self, access_token: str, start_date: date, end_date: date) -> List[Dict]:
        """거래 내역 조회"""
        pass

