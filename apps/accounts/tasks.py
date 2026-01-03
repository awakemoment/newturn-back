"""
계좌 관련 Celery 작업

주가 업데이트 등 백그라운드 작업
"""
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import logging

from apps.accounts.models import SavingsReward
from apps.broker.factory import get_broker_api

logger = logging.getLogger(__name__)


@shared_task(name='accounts.update_reward_prices')
def update_reward_prices():
    """
    모든 투자 중인 SavingsReward의 주가를 업데이트
    
    매일 실행되어 현재가를 조회하고 가치를 재계산
    """
    try:
        # 투자 중인 모든 리워드 가져오기
        rewards = SavingsReward.objects.filter(status='invested').select_related('stock')
        
        if not rewards.exists():
            logger.info("업데이트할 투자가 없습니다.")
            return {
                'success': True,
                'updated_count': 0,
                'message': '업데이트할 투자가 없습니다.'
            }
        
        # 브로커 API 가져오기 (시뮬레이션 또는 실제)
        broker = get_broker_api(force_simulation=None)
        
        updated_count = 0
        error_count = 0
        errors = []
        
        for reward in rewards:
            try:
                symbol = reward.stock.stock_code
                
                # 현재가 조회
                current_price = broker.get_current_price(symbol)
                
                # 트랜잭션 내에서 업데이트
                with transaction.atomic():
                    reward.current_price = Decimal(str(current_price))
                    reward.update_current_value()  # 가치 재계산
                    updated_count += 1
                    
                logger.info(f"✅ {symbol} 업데이트 완료: ${current_price} (리워드 ID: {reward.id})")
                
            except Exception as e:
                error_count += 1
                error_msg = f"리워드 ID {reward.id} ({reward.stock.stock_code}) 업데이트 실패: {str(e)}"
                logger.error(f"❌ {error_msg}")
                errors.append(error_msg)
                continue
        
        result = {
            'success': True,
            'updated_count': updated_count,
            'error_count': error_count,
            'total_count': rewards.count(),
            'errors': errors if errors else None,
        }
        
        logger.info(f"주가 업데이트 완료: {updated_count}개 성공, {error_count}개 실패")
        return result
        
    except Exception as e:
        error_msg = f"주가 업데이트 작업 실패: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            'success': False,
            'error': error_msg,
        }


@shared_task(name='accounts.update_single_reward_price')
def update_single_reward_price(reward_id: int):
    """
    단일 SavingsReward의 주가 업데이트
    
    Args:
        reward_id: SavingsReward ID
    """
    try:
        reward = SavingsReward.objects.select_related('stock').get(id=reward_id, status='invested')
        
        symbol = reward.stock.stock_code
        broker = get_broker_api(force_simulation=None)
        
        # 현재가 조회
        current_price = broker.get_current_price(symbol)
        
        # 트랜잭션 내에서 업데이트
        with transaction.atomic():
            reward.current_price = Decimal(str(current_price))
            reward.update_current_value()
        
        logger.info(f"✅ {symbol} 업데이트 완료: ${current_price} (리워드 ID: {reward.id})")
        
        return {
            'success': True,
            'reward_id': reward_id,
            'symbol': symbol,
            'current_price': float(current_price),
        }
        
    except SavingsReward.DoesNotExist:
        error_msg = f"리워드 ID {reward_id}를 찾을 수 없습니다."
        logger.error(f"❌ {error_msg}")
        return {
            'success': False,
            'error': error_msg,
        }
    except Exception as e:
        error_msg = f"리워드 ID {reward_id} 업데이트 실패: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            'success': False,
            'error': error_msg,
        }

