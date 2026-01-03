from django.contrib import admin
from .models import (
    CategoryAccount, Transaction, SavingsReward,
    UserBankAccount, DepositAccount, DepositTransaction
)


@admin.register(CategoryAccount)
class CategoryAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'category', 'balance', 'monthly_budget', 'current_month_spent', 'is_active']
    list_filter = ['category', 'is_active', 'auto_sync_enabled']
    search_fields = ['user__username', 'name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'transaction_type', 'amount', 'balance_after', 'transaction_date', 'is_synced_from_bank']
    list_filter = ['transaction_type', 'is_synced_from_bank', 'transaction_date']
    search_fields = ['account__name', 'merchant_name', 'note']
    readonly_fields = ['transaction_date']


@admin.register(SavingsReward)
class SavingsRewardAdmin(admin.ModelAdmin):
    list_display = ['account', 'stock', 'savings_amount', 'status', 'return_rate', 'is_profitable', 'can_sell']
    list_filter = ['status', 'is_profitable', 'can_sell']
    search_fields = ['account__name', 'stock__stock_code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserBankAccount)
class UserBankAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'bank_name', 'account_name', 'account_type', 'is_active', 'is_primary']
    list_filter = ['bank_name', 'account_type', 'is_active', 'is_primary']
    search_fields = ['user__username', 'bank_name', 'account_name']
    readonly_fields = ['created_at', 'updated_at', 'last_synced_at']


@admin.register(DepositAccount)
class DepositAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'account_number', 'balance', 'total_deposited', 'total_withdrawn', 'is_active']
    list_filter = ['is_active']
    search_fields = ['user__username', 'account_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DepositTransaction)
class DepositTransactionAdmin(admin.ModelAdmin):
    list_display = ['deposit_account', 'transaction_type', 'amount', 'balance_after', 'transaction_date']
    list_filter = ['transaction_type', 'transaction_date']
    search_fields = ['deposit_account__account_number', 'note']
    readonly_fields = ['transaction_date']

