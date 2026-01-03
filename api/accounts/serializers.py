"""
계좌 관련 Serializers
"""
from rest_framework import serializers
from apps.accounts.models import (
    CategoryAccount, Transaction, SavingsReward,
    UserBankAccount, DepositAccount, DepositTransaction
)
from apps.stocks.models import Stock


class StockBasicSerializer(serializers.ModelSerializer):
    """종목 기본 정보 (중첩용)"""
    class Meta:
        model = Stock
        fields = ['id', 'stock_code', 'stock_name']


class CategoryAccountSerializer(serializers.ModelSerializer):
    """카테고리 통장 Serializer"""
    linked_bank_account_info = serializers.SerializerMethodField()
    
    class Meta:
        model = CategoryAccount
        fields = [
            'id', 'name', 'category', 'balance', 'total_deposited',
            'monthly_budget', 'current_month_spent',
            'total_savings_reward', 'pending_reward', 'realized_reward',
            'linked_bank_account', 'linked_bank_account_info', 'auto_sync_enabled', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'balance', 'total_deposited', 'current_month_spent',
            'total_savings_reward', 'pending_reward', 'realized_reward',
            'created_at', 'updated_at',
        ]

    def get_linked_bank_account_info(self, obj):
        """연동된 은행 계좌 정보"""
        if obj.linked_bank_account:
            return {
                'id': obj.linked_bank_account.id,
                'bank_name': obj.linked_bank_account.bank_name,
                'account_name': obj.linked_bank_account.account_name,
                'account_number_masked': obj.linked_bank_account.account_number_masked,
            }
        return None

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TransactionSerializer(serializers.ModelSerializer):
    """거래 내역 Serializer"""
    class Meta:
        model = Transaction
        fields = [
            'id', 'account', 'transaction_type', 'amount', 'balance_after',
            'merchant_name', 'category_detail', 'note',
            'plaid_transaction_id', 'is_synced_from_bank',
            'transaction_date', 'bank_transaction_date',
        ]
        read_only_fields = ['balance_after', 'transaction_date']


class SavingsRewardSerializer(serializers.ModelSerializer):
    """절약 리워드 Serializer"""
    stock = StockBasicSerializer(read_only=True)
    stock_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = SavingsReward
        fields = [
            'id', 'account', 'savings_amount', 'period_start', 'period_end',
            'budget', 'actual_spent', 'stock', 'stock_id',
            'purchase_price', 'purchase_date', 'shares',
            'current_price', 'current_value', 'return_rate', 'is_profitable',
            'can_sell', 'sell_price', 'sell_date', 'commission', 'net_proceeds',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'purchase_price', 'purchase_date', 'shares',
            'current_price', 'current_value', 'return_rate', 'is_profitable',
            'can_sell', 'sell_price', 'sell_date', 'commission', 'net_proceeds',
            'status', 'created_at', 'updated_at',
        ]


class UserBankAccountSerializer(serializers.ModelSerializer):
    """은행 계좌 Serializer"""
    class Meta:
        model = UserBankAccount
        fields = [
            'id', 'bank_name', 'account_name', 'account_type',
            'account_number_masked', 'current_balance', 'available_balance',
            'is_active', 'is_primary', 'is_simulation', 'last_synced_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'current_balance', 'available_balance', 'last_synced_at',
            'created_at', 'updated_at',
        ]


class DepositAccountSerializer(serializers.ModelSerializer):
    """예치금 계좌 Serializer"""
    class Meta:
        model = DepositAccount
        fields = [
            'id', 'account_number', 'balance', 'total_deposited', 'total_withdrawn',
            'alpaca_account_id', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'account_number', 'balance', 'total_deposited', 'total_withdrawn',
            'created_at', 'updated_at',
        ]

