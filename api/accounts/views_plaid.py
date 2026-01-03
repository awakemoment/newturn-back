"""
Plaid 은행 계좌 연동 API Views
"""
from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction as db_transaction

from apps.accounts.models import UserBankAccount
from apps.accounts.services.plaid_service import PlaidIntegrationService
from apps.broker.factory import get_bank_api
from .serializers import UserBankAccountSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_link_token(request):
    """
    Plaid Link Token 생성
    
    POST /api/accounts/plaid/link-token/
    """
    try:
        bank_api = get_bank_api()
        user_id = str(request.user.id)
        link_token = bank_api.create_link_token(user_id)
        
        return Response({
            'link_token': link_token,
            'expiration': None,  # 시뮬레이션에서는 만료 없음
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def exchange_public_token(request):
    """
    Public Token을 Access Token으로 교환하고 계좌 정보 저장
    
    POST /api/accounts/plaid/exchange-token/
    {
        "public_token": "public-sandbox-xxx",
        "institution_id": "ins_109508",  # Wells Fargo
        "accounts": [
            {
                "id": "account_id_1",
                "name": "Checking Account",
                "mask": "1234"
            }
        ]
    }
    """
    public_token = request.data.get('public_token')
    institution_id = request.data.get('institution_id')
    accounts = request.data.get('accounts', [])
    
    if not public_token:
        return Response(
            {'error': 'public_token이 필요합니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        bank_api = get_bank_api()
        
        # 시뮬레이션 모드 판단
        from apps.broker.simulation import SimulationBankAPI
        is_simulation = isinstance(bank_api, SimulationBankAPI)
        
        # Public Token → Access Token 교환
        access_token = bank_api.exchange_public_token(public_token)
        
        # 계좌 정보 조회
        plaid_accounts = bank_api.get_accounts(access_token)
        
        # UserBankAccount 생성
        created_accounts = []
        with db_transaction.atomic():
            for account_data in accounts:
                account_id_from_frontend = account_data.get('id')
                
                # Plaid에서 받은 계좌 정보 찾기
                plaid_account = next(
                    (acc for acc in plaid_accounts if acc['account_id'] == account_id_from_frontend),
                    None
                )
                
                # 매칭되지 않으면 프론트엔드에서 보낸 정보 사용
                if not plaid_account:
                    # 프론트엔드에서 보낸 계좌 정보로 계좌 생성
                    plaid_account = {
                        'account_id': account_id_from_frontend,
                        'name': account_data.get('name', 'Unknown Account'),
                        'type': 'depository',
                        'subtype': 'checking',
                        'balance': Decimal('0'),
                        'mask': account_data.get('mask', '****'),
                    }
                
                # 은행명 결정 (Wells Fargo)
                # institution_id로부터 은행명 결정 가능
                institution_names = {
                    'ins_109508': 'Wells Fargo',
                    'ins_109509': 'Chase',
                    'ins_109510': 'Bank of America',
                }
                bank_name = institution_names.get(institution_id, 'Wells Fargo')
                
                # UserBankAccount 생성 또는 업데이트
                bank_account, created = UserBankAccount.objects.update_or_create(
                    user=request.user,
                    plaid_account_id=plaid_account['account_id'],
                    defaults={
                        'plaid_access_token': access_token,
                        'plaid_item_id': institution_id,  # 실제로는 item_id
                        'bank_name': bank_name,
                        'account_name': plaid_account.get('name', account_data.get('name', '')),
                        'account_type': plaid_account.get('subtype', account_data.get('type', 'checking')),
                        'account_number_masked': plaid_account.get('mask', account_data.get('mask', '****')),
                        'current_balance': plaid_account.get('balance', Decimal('0')),
                        'available_balance': plaid_account.get('balance', Decimal('0')),
                        'is_active': True,
                        'is_simulation': is_simulation,
                    }
                )
                
                # Serializer로 직렬화 (refresh 필요)
                bank_account.refresh_from_db()
                created_accounts.append(UserBankAccountSerializer(bank_account).data)
        
        return Response({
            'success': True,
            'accounts': created_accounts,
            'message': f'{len(created_accounts)}개의 계좌가 연동되었습니다.',
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserBankAccountViewSet(viewsets.ModelViewSet):
    """은행 계좌 조회 및 삭제"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserBankAccountSerializer
    
    def get_queryset(self):
        queryset = UserBankAccount.objects.filter(user=self.request.user, is_active=True)
        print(f"🔍 UserBankAccount 쿼리셋: {queryset.count()}개 (User: {self.request.user.username})")
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        """은행 계좌 삭제 (소프트 삭제)"""
        bank_account = self.get_object()
        
        # 연동된 카테고리 통장이 있는지 확인
        from apps.accounts.models import CategoryAccount
        linked_accounts = CategoryAccount.objects.filter(
            linked_bank_account=bank_account,
            user=request.user
        )
        
        if linked_accounts.exists():
            account_names = ', '.join([acc.name for acc in linked_accounts[:3]])
            return Response(
                {'error': f'다음 카테고리 통장에 연동되어 있어 삭제할 수 없습니다: {account_names}' + (' 등' if linked_accounts.count() > 3 else '')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 소프트 삭제
        bank_account.is_active = False
        bank_account.save()
        
        return Response({
            'success': True,
            'message': '은행 계좌가 삭제되었습니다.',
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='transactions')
    def transactions(self, request, pk=None):
        """은행 계좌의 거래 내역 조회"""
        bank_account = self.get_object()
        
        from apps.accounts.models import Transaction
        transactions = Transaction.objects.filter(
            plaid_transaction_id__isnull=False,
            account__linked_bank_account=bank_account
        ).order_by('-bank_transaction_date', '-transaction_date')
        
        from .serializers import TransactionSerializer
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def sync_transactions(self, request, pk=None):
        """거래 내역 동기화"""
        bank_account = self.get_object()
        
        try:
            service = PlaidIntegrationService()
            service.sync_bank_transactions(bank_account)
            
            return Response({
                'success': True,
                'message': '거래 내역이 동기화되었습니다.',
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

