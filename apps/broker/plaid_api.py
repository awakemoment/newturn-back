"""
실제 Plaid API 구현

BankAPIInterface를 구현하여 시뮬레이션과 동일한 인터페이스 제공
"""
import os
from decimal import Decimal
from typing import List, Dict
from datetime import date
from plaid.api import plaid_api
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid import ApiException

from .interfaces import BankAPIInterface


class PlaidBankAPI(BankAPIInterface):
    """실제 Plaid API 구현 (BankAPIInterface)"""
    
    def __init__(self):
        """Plaid API 초기화"""
        self.client_id = os.getenv('PLAID_CLIENT_ID')
        self.secret = os.getenv('PLAID_SECRET')
        self.env = os.getenv('PLAID_ENV', 'sandbox')
        
        if not self.client_id or not self.secret:
            raise ValueError("Plaid API 키가 설정되지 않았습니다.")
        
        # 환경 설정
        environments = {
            'sandbox': plaid.Environment.sandbox,
            'development': plaid.Environment.development,
            'production': plaid.Environment.production,
        }
        
        configuration = Configuration(
            host=environments.get(self.env, plaid.Environment.sandbox),
            api_key={
                'clientId': self.client_id,
                'secret': self.secret,
            }
        )
        
        api_client = ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)
    
    def create_link_token(self, user_id: str) -> str:
        """Link Token 생성"""
        from plaid.model.link_token_create_request import LinkTokenCreateRequest
        from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
        
        request = LinkTokenCreateRequest(
            products=[Products('auth'), Products('transactions')],
            client_name='Newturn',
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id=user_id
            )
        )
        
        response = self.client.link_token_create(request)
        return response['link_token']
    
    def exchange_public_token(self, public_token: str) -> str:
        """Public Token을 Access Token으로 교환"""
        from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
        
        request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        
        response = self.client.item_public_token_exchange(request)
        return response['access_token']
    
    def get_accounts(self, access_token: str) -> List[Dict]:
        """연결된 계좌 목록 조회"""
        from plaid.model.accounts_get_request import AccountsGetRequest
        
        request = AccountsGetRequest(access_token=access_token)
        response = self.client.accounts_get(request)
        
        return [
            {
                'account_id': acc['account_id'],
                'name': acc['name'],
                'type': acc['type'],
                'subtype': acc.get('subtype'),
                'balance': Decimal(str(acc['balances']['available'] or 0)),
                'mask': acc.get('mask', ''),
                'institution_name': acc.get('institution_name', ''),
            }
            for acc in response['accounts']
        ]
    
    def get_account_balance(self, access_token: str, account_id: str) -> Decimal:
        """특정 계좌 잔액 조회"""
        accounts = self.get_accounts(access_token)
        account = next((acc for acc in accounts if acc['account_id'] == account_id), None)
        
        if not account:
            raise ValueError(f"계좌를 찾을 수 없습니다: {account_id}")
        
        return account['balance']
    
    def get_transactions(self, access_token: str, start_date: date, end_date: date) -> List[Dict]:
        """거래 내역 조회"""
        from plaid.model.transactions_get_request import TransactionsGetRequest
        from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
        
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=TransactionsGetRequestOptions(
                count=500,
                offset=0
            )
        )
        
        response = self.client.transactions_get(request)
        
        return [
            {
                'transaction_id': txn['transaction_id'],
                'name': txn['name'],
                'merchant_name': txn.get('merchant_name'),
                'amount': Decimal(str(txn['amount'])),
                'date': txn['date'],
                'authorized_date': txn.get('authorized_date'),
                'category': txn.get('category', []),
            }
            for txn in response['transactions']
        ]

