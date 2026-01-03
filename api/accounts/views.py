"""
계좌 관리 API Views
"""
from decimal import Decimal
from django.utils import timezone
from django.db import transaction as db_transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import (
    CategoryAccount, Transaction, SavingsReward,
    DepositAccount
)
from apps.accounts.services.trading_service import TradingService
from .serializers import (
    CategoryAccountSerializer, TransactionSerializer, SavingsRewardSerializer,
    DepositAccountSerializer
)


class CategoryAccountViewSet(viewsets.ModelViewSet):
    """카테고리별 통장 관리"""
    permission_classes = [IsAuthenticated]
    serializer_class = CategoryAccountSerializer

    def get_queryset(self):
        queryset = CategoryAccount.objects.filter(user=self.request.user, is_active=True)
        print(f"🔍 CategoryAccount 쿼리셋: {queryset.count()}개 (User: {self.request.user.username})")
        return queryset

    def destroy(self, request, *args, **kwargs):
        """카테고리 통장 삭제 (소프트 삭제)"""
        account = self.get_object()
        
        # 투자 중인 SavingsReward가 있는지 확인
        active_rewards = SavingsReward.objects.filter(
            account=account,
            status='invested'
        )
        
        if active_rewards.exists():
            return Response(
                {'error': '투자 중인 절약 리워드가 있어 삭제할 수 없습니다. 먼저 투자를 정리해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 소프트 삭제
        account.is_active = False
        account.linked_bank_account = None  # 연동 해제
        account.auto_sync_enabled = False
        account.save()
        
        return Response({
            'success': True,
            'message': '카테고리 통장이 삭제되었습니다.',
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def deposit(self, request, pk=None):
        """입금"""
        account = self.get_object()
        amount = Decimal(str(request.data.get('amount', 0)))

        if amount <= 0:
            return Response(
                {'error': '입금액은 0보다 커야 합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with db_transaction.atomic():
            account.balance += amount
            account.total_deposited += amount
            account.save()

            Transaction.objects.create(
                account=account,
                transaction_type='deposit',
                amount=amount,
                balance_after=account.balance,
                note=request.data.get('note', '')
            )

        return Response(CategoryAccountSerializer(account).data)

    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        """출금 (소비)"""
        account = self.get_object()
        amount = Decimal(str(request.data.get('amount', 0)))
        merchant_name = request.data.get('merchant_name', '')
        category_detail = request.data.get('category_detail', '')
        note = request.data.get('note', '')

        if amount <= 0:
            return Response(
                {'error': '출금액은 0보다 커야 합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if account.balance < amount:
            return Response(
                {'error': '잔액이 부족합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with db_transaction.atomic():
            account.balance -= amount
            account.current_month_spent += amount
            account.save()

            Transaction.objects.create(
                account=account,
                transaction_type='withdrawal',
                amount=amount,
                balance_after=account.balance,
                merchant_name=merchant_name,
                category_detail=category_detail,
                note=note
            )

        return Response(CategoryAccountSerializer(account).data)

    @action(detail=True, methods=['get'], url_path='monthly-savings')
    def monthly_savings(self, request, pk=None):
        """월간 절약 금액 계산"""
        account = self.get_object()
        savings = account.calculate_monthly_savings()
        return Response({'savings': float(savings)})

    @action(detail=True, methods=['post'], url_path='invest-savings')
    def invest_savings(self, request, pk=None):
        """절약 금액으로 주식 투자"""
        account = self.get_object()
        stock_id = request.data.get('stock_id')

        if not stock_id:
            return Response(
                {'error': 'stock_id가 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 절약 금액 확인
        savings = account.calculate_monthly_savings()
        if savings <= 0:
            return Response(
                {'error': '절약 금액이 없습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from apps.stocks.models import Stock
            stock = Stock.objects.get(id=stock_id)

            # 예치금 계좌 가져오기 또는 생성
            deposit_account, _ = DepositAccount.objects.get_or_create(
                user=request.user,
                defaults={'account_number': f'DEP-{request.user.id}'}
            )

            # 투자 서비스 사용
            trading_service = TradingService(deposit_account=deposit_account)

            # SavingsReward 생성
            reward = SavingsReward.objects.create(
                account=account,
                savings_amount=savings,
                period_start=timezone.now().replace(day=1).date(),
                period_end=timezone.now().date(),
                budget=account.monthly_budget or Decimal('0'),
                actual_spent=account.current_month_spent,
                stock=stock,
                purchase_price=Decimal('0'),  # 나중에 업데이트
                purchase_date=timezone.now(),
                shares=Decimal('0'),  # 나중에 업데이트
                status='pending'
            )

            # 실제 투자 실행
            reward = trading_service.execute_investment(reward)

            # 계좌 업데이트
            account.pending_reward += savings
            account.current_month_spent = Decimal('0')  # 다음 달을 위해 초기화
            account.save()

            return Response(
                SavingsRewardSerializer(reward).data,
                status=status.HTTP_201_CREATED
            )

        except Stock.DoesNotExist:
            return Response(
                {'error': '종목을 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"❌ 투자 실행 에러: {str(e)}")
            print(f"❌ 에러 상세:\n{error_trace}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """거래 내역 조회"""
        account = self.get_object()
        transactions = Transaction.objects.filter(account=account).order_by('-transaction_date')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='link-bank-account')
    def link_bank_account(self, request, pk=None):
        """카테고리 통장과 은행 계좌 연결"""
        account = self.get_object()
        bank_account_id = request.data.get('bank_account_id')
        auto_sync = request.data.get('auto_sync_enabled', False)
        
        if not bank_account_id:
            return Response(
                {'error': 'bank_account_id가 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.accounts.models import UserBankAccount
            bank_account = UserBankAccount.objects.get(id=bank_account_id, user=request.user)
            
            account.linked_bank_account = bank_account
            account.auto_sync_enabled = auto_sync
            account.save()
            
            return Response(CategoryAccountSerializer(account).data)
        except UserBankAccount.DoesNotExist:
            return Response(
                {'error': '은행 계좌를 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], url_path='unlink-bank-account')
    def unlink_bank_account(self, request, pk=None):
        """카테고리 통장과 은행 계좌 연결 해제"""
        account = self.get_object()
        
        if not account.linked_bank_account:
            return Response(
                {'error': '연동된 은행 계좌가 없습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        account.linked_bank_account = None
        account.auto_sync_enabled = False
        account.save()
        
        return Response(CategoryAccountSerializer(account).data)
    
    @action(detail=True, methods=['post'], url_path='sync-transactions')
    def sync_transactions(self, request, pk=None):
        """연동된 은행 계좌의 거래 내역 동기화"""
        account = self.get_object()
        
        if not account.linked_bank_account:
            return Response(
                {'error': '연동된 은행 계좌가 없습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.accounts.services.plaid_service import PlaidIntegrationService
            service = PlaidIntegrationService()
            service.sync_bank_transactions(account.linked_bank_account)
            
            # 계좌 정보 새로고침
            account.refresh_from_db()
            
            return Response({
                'success': True,
                'message': '거래 내역이 동기화되었습니다.',
                'account': CategoryAccountSerializer(account).data,
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class SavingsRewardViewSet(viewsets.ReadOnlyModelViewSet):
    """절약 리워드 (투자) 조회"""
    permission_classes = [IsAuthenticated]
    serializer_class = SavingsRewardSerializer

    def get_queryset(self):
        return SavingsReward.objects.filter(account__user=self.request.user)

    @action(detail=True, methods=['post'])
    def sell(self, request, pk=None):
        """매도 (수익일 때만)"""
        reward = self.get_object()

        if not reward.can_sell:
            return Response(
                {'error': '손실 상태에서는 매도할 수 없습니다. 보유를 유지해야 합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 예치금 계좌 가져오기
            deposit_account = DepositAccount.objects.filter(user=request.user).first()
            if not deposit_account:
                return Response(
                    {'error': '예치금 계좌가 없습니다.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 투자 서비스 사용
            trading_service = TradingService(deposit_account=deposit_account)
            reward, net_proceeds = trading_service.execute_sale(reward)

            return Response({
                'success': True,
                'net_proceeds': float(net_proceeds),
                'return_rate': float(reward.return_rate) if reward.return_rate else 0,
                'reward': SavingsRewardSerializer(reward).data,
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class DepositAccountViewSet(viewsets.ReadOnlyModelViewSet):
    """예치금 계좌 조회"""
    permission_classes = [IsAuthenticated]
    serializer_class = DepositAccountSerializer

    def get_queryset(self):
        return DepositAccount.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """현재 사용자의 예치금 계좌 조회 (또는 생성)"""
        deposit_account, created = DepositAccount.objects.get_or_create(
            user=request.user,
            defaults={'account_number': f'DEP-{request.user.id}'}
        )
        return Response(DepositAccountSerializer(deposit_account).data)

