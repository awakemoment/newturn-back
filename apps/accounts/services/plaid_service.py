"""
Plaid 연동 서비스 (은행 API 추상화 사용)

시뮬레이션/실제 API를 동일한 방식으로 사용
"""
from decimal import Decimal
from typing import List, Dict
from datetime import date, timedelta
from django.utils import timezone
from django.db import transaction as db_transaction

from apps.broker.factory import get_bank_api
from apps.accounts.models import UserBankAccount, CategoryAccount, Transaction


class PlaidIntegrationService:
    """Plaid 연동 서비스 (은행 API 추상화)"""
    
    def __init__(self):
        self.bank_api = get_bank_api()
    
    def sync_bank_transactions(self, user_bank_account: UserBankAccount):
        """
        은행 거래 내역 동기화
        
        Args:
            user_bank_account: UserBankAccount 객체
        """
        # Plaid Transactions API로 최근 거래 조회
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        transactions = self.bank_api.get_transactions(
            access_token=user_bank_account.plaid_access_token,
            start_date=start_date,
            end_date=end_date
        )
        
        # 연동된 카테고리 통장들 찾기
        category_accounts = CategoryAccount.objects.filter(
            linked_bank_account=user_bank_account,
            auto_sync_enabled=True
        )
        
        for plaid_txn in transactions:
            # 이미 동기화된 거래인지 확인
            existing = Transaction.objects.filter(
                plaid_transaction_id=plaid_txn['transaction_id']
            ).first()
            
            if existing:
                continue  # 이미 동기화됨
            
            # 카테고리 매핑
            category_account = self._match_category(
                plaid_txn,
                category_accounts
            )
            
            if not category_account:
                continue  # 매칭되는 카테고리 없음
            
            # Transaction 생성 (트랜잭션 내에서)
            amount = abs(plaid_txn['amount'])
            is_debit = plaid_txn['amount'] < 0  # 출금인 경우
            
            with db_transaction.atomic():
                # 잔액 계산
                if is_debit:
                    new_balance = category_account.balance - amount
                else:
                    new_balance = category_account.balance + amount
                
                Transaction.objects.create(
                    account=category_account,
                    transaction_type='bank_sync' if is_debit else 'deposit',
                    amount=amount,
                    balance_after=new_balance,
                    merchant_name=plaid_txn.get('merchant_name', ''),
                    category_detail=str(plaid_txn.get('category', [])),
                    plaid_transaction_id=plaid_txn['transaction_id'],
                    bank_transaction_id=str(plaid_txn.get('authorized_date', '')),
                    is_synced_from_bank=True,
                    bank_transaction_date=plaid_txn.get('date') if isinstance(plaid_txn.get('date'), date) else None,
                    note=f"자동 동기화: {plaid_txn.get('name', '')}"
                )
                
                # CategoryAccount 업데이트
                if is_debit:
                    category_account.balance = new_balance
                    category_account.current_month_spent += amount
                else:
                    category_account.balance = new_balance
                    category_account.total_deposited += amount
                
                category_account.save()
        
        # 마지막 동기화 시간 업데이트
        user_bank_account.last_synced_at = timezone.now()
        user_bank_account.save()
    
    def _match_category(self, plaid_transaction: Dict, category_accounts) -> CategoryAccount:
        """
        Plaid 거래를 카테고리 통장에 자동 매칭
        
        Args:
            plaid_transaction: Plaid 거래 데이터
            category_accounts: CategoryAccount 쿼리셋
        
        Returns:
            매칭된 CategoryAccount 또는 None
        """
        merchant_name = (plaid_transaction.get('merchant_name') or '').lower()
        transaction_name = (plaid_transaction.get('name') or '').lower()
        categories = plaid_transaction.get('category', [])
        
        # 1. 사용자 정의 규칙 매칭
        for account in category_accounts:
            rules = account.sync_category_rules or {}
            
            # merchant_name 매칭
            if 'merchant_name_contains' in rules:
                keywords = rules['merchant_name_contains']
                if any(keyword.lower() in merchant_name or keyword.lower() in transaction_name 
                       for keyword in keywords):
                    return account
            
            # category 매칭
            if 'category' in rules:
                if rules['category'] in categories:
                    return account
        
        # 2. 자동 분류 (규칙이 없을 때)
        # 카테고리 기반 자동 매칭
        category_mapping = {
            'coffee': {
                'merchants': ['starbucks', 'dunkin', 'coffee', 'cafe', 'peets', 'blue bottle'],
                'categories': ['Food and Drink', 'Restaurants', 'Coffee Shops'],
            },
            'snack': {
                'merchants': ['7-eleven', 'cvs', 'walgreens', 'convenience'],
                'categories': ['Food and Drink', 'Groceries'],
            },
            'subscription': {
                'merchants': ['netflix', 'spotify', 'amazon prime', 'apple', 'google'],
                'categories': ['Shops', 'Digital Purchase', 'Entertainment'],
            },
            'entertainment': {
                'merchants': ['movie', 'theater', 'cinema', 'amc', 'regal'],
                'categories': ['Entertainment', 'Recreation'],
            },
            'shopping': {
                'merchants': ['amazon', 'target', 'walmart', 'costco'],
                'categories': ['Shops', 'Department Stores'],
            },
        }
        
        for account in category_accounts:
            account_category = account.category
            if account_category in category_mapping:
                mapping = category_mapping[account_category]
                
                # merchant_name 매칭
                if any(merchant in merchant_name or merchant in transaction_name 
                       for merchant in mapping['merchants']):
                    return account
                
                # category 매칭
                if any(cat in str(categories) for cat in mapping['categories']):
                    return account
        
        return None

