"""
관심 종목(Watchlist) API
"""
from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

from apps.watchlist.models import Watchlist
from apps.stocks.models import StockFinancialRaw, StockPrice
from apps.analysis.models import ProperPrice, MateAnalysis
from .serializers import WatchlistSerializer
from core.utils.valuation_engine import calculate_all_mates_proper_price

User = get_user_model()


class WatchlistViewSet(viewsets.ModelViewSet):
    """
    관심 종목 API
    
    - list: 내 관심 종목 목록
    - create: 관심 종목 추가
    - retrieve: 관심 종목 상세
    - update: 관심 종목 수정
    - destroy: 관심 종목 삭제
    - signals: 매수/매도 시그널 (전체 관심 종목)
    """
    permission_classes = [AllowAny]  # 임시로 로그인 없이 사용 가능
    serializer_class = WatchlistSerializer
    
    def get_queryset(self):
        """사용자 본인의 관심 종목만 조회"""
        user = self.request.user if self.request.user.is_authenticated else self._get_dev_user()
        return Watchlist.objects.filter(user=user).select_related('stock')
    
    def _get_dev_user(self):
        """개발용 임시 사용자"""
        user, _ = User.objects.get_or_create(
            username='dev_user',
            defaults={
                'email': 'dev@newturn.com',
                'first_name': 'Dev',
                'last_name': 'User',
            }
        )
        return user
    
    def perform_create(self, serializer):
        """관심 종목 추가 시 적정가격 자동 계산"""
        user = self.request.user if self.request.user.is_authenticated else self._get_dev_user()
        watchlist = serializer.save(user=user)
        
        # 적정가격 계산 (백그라운드에서 비동기로 하는 게 좋지만 일단 동기)
        self._calculate_proper_prices(watchlist.stock)
    
    def _get_recommendation(self, gap_ratio):
        """괴리율에 따른 분석 결과 (참고용)"""
        if gap_ratio <= -20:
            return "🟢 20% 이상 저평가 (참고)"
        elif gap_ratio <= -10:
            return "🟢 10% 이상 저평가 (참고)"
        elif gap_ratio <= 10:
            return "🟡 적정가 범위 (±10%)"
        elif gap_ratio <= 20:
            return "🟠 10% 이상 고평가"
        else:
            return "🔴 20% 이상 고평가"
    
    def _calculate_proper_prices(self, stock):
        """종목의 적정가격 계산 (4개 메이트 모두)"""
        try:
            # 재무 지표 계산
            recent_4q = list(StockFinancialRaw.objects.filter(
                stock=stock,
                data_source='EDGAR'
            ).order_by('-disclosure_year', '-disclosure_quarter')[:4])
            
            if len(recent_4q) < 4:
                print(f"⚠️ {stock.stock_code}: 재무 데이터 부족 (적정가격 계산 생략)")
                return
            
            ttm_fcf = sum([q.fcf or 0 for q in recent_4q])
            ttm_net_income = sum([q.net_income or 0 for q in recent_4q])
            ttm_revenue = sum([q.revenue or 0 for q in recent_4q])
            
            latest = recent_4q[0]
            
            # 성장률
            previous_4q = list(StockFinancialRaw.objects.filter(
                stock=stock,
                data_source='EDGAR'
            ).order_by('-disclosure_year', '-disclosure_quarter')[4:8])
            
            revenue_growth = 0
            if len(previous_4q) == 4:
                prev_revenue = sum([q.revenue or 0 for q in previous_4q])
                if prev_revenue:
                    revenue_growth = ((ttm_revenue - prev_revenue) / prev_revenue) * 100
            
            indicators = {
                'ttm_fcf': ttm_fcf,
                'ttm_net_income': ttm_net_income,
                'total_equity': latest.total_equity,
                'revenue_growth': revenue_growth,
            }
            
            # 현재가
            latest_price = StockPrice.objects.filter(stock=stock).order_by('-date').first()
            if not latest_price:
                print(f"⚠️ {stock.stock_code}: 주가 데이터 없음 (적정가격 계산 생략)")
                return
            
            current_price = float(latest_price.close_price)
            
            # 발행주식수
            shares_outstanding = stock.shares_outstanding if stock.shares_outstanding else 1000000000  # 없으면 10억주 가정
            
            # 4개 메이트 적정가격 계산
            valuations = calculate_all_mates_proper_price(indicators, current_price, shares_outstanding)
            
            # DB 저장
            for mate_type, valuation in valuations.items():
                ProperPrice.objects.update_or_create(
                    stock=stock,
                    mate_type=mate_type,
                    defaults={
                        'proper_price': valuation['proper_price'],
                        'current_price': Decimal(str(current_price)),
                        'gap_ratio': valuation['gap_ratio'],
                        'calculation_method': valuation['method'],
                    }
                )
            print(f"✅ {stock.stock_code}: 적정가격 계산 완료 (4개 메이트)")
        except Exception as e:
            print(f"❌ {stock.stock_code}: 적정가격 계산 실패 - {e}")
            import traceback
            traceback.print_exc()
    
    @action(detail=False, methods=['get'])
    def signals(self, request):
        """
        매수/매도 시그널 (전체 관심 종목)
        
        Response:
        {
          "buy_signals": [
            {
              "watchlist_id": 1,
              "stock": {...},
              "current_price": 100.0,
              "proper_price": 120.0,
              "gap_ratio": -16.7,
              "signal": "강력 매수",
              "mate": "benjamin"
            }
          ],
          "sell_signals": [...],
          "hold_signals": [...]
        }
        """
        watchlist_items = self.get_queryset()
        
        buy_signals = []
        sell_signals = []
        hold_signals = []
        
        for item in watchlist_items:
            stock = item.stock
            
            # 최신 주가
            latest_price = StockPrice.objects.filter(stock=stock).order_by('-date').first()
            if not latest_price:
                continue
            
            current_price = float(latest_price.close_price)
            
            # 선호 메이트의 적정가격 (없으면 benjamin)
            preferred_mate = item.preferred_mate or 'benjamin'
            
            try:
                proper_price_obj = ProperPrice.objects.get(stock=stock, mate_type=preferred_mate)
                proper_price = float(proper_price_obj.proper_price)
                gap_ratio = float(proper_price_obj.gap_ratio)
                
                # 모든 메이트의 적정가격 가져오기
                all_proper_prices = ProperPrice.objects.filter(stock=stock)
                all_proper_prices_data = [
                    {
                        'mate_type': pp.mate_type,
                        'proper_price': float(pp.proper_price),
                        'current_price': float(pp.current_price),
                        'gap_ratio': float(pp.gap_ratio),
                        'calculation_method': pp.calculation_method,
                        'recommendation': self._get_recommendation(float(pp.gap_ratio)),
                    }
                    for pp in all_proper_prices
                ]
                
                signal_data = {
                    'watchlist_id': item.id,
                    'stock': {
                        'id': stock.id,
                        'stock_code': stock.stock_code,
                        'stock_name': stock.stock_name,
                    },
                    'current_price': current_price,
                    'proper_price': proper_price,
                    'gap_ratio': gap_ratio,
                    'mate': preferred_mate,
                    'all_proper_prices': all_proper_prices_data,  # 모든 메이트 적정가격
                }
                
                # 분석 결과 분류
                if gap_ratio <= -10:
                    signal_data['signal'] = '20% 이상 저평가' if gap_ratio <= -20 else '10% 이상 저평가'
                    signal_data['icon'] = '🟢'
                    buy_signals.append(signal_data)
                elif gap_ratio >= 20:
                    signal_data['signal'] = '20% 이상 고평가'
                    signal_data['icon'] = '🔴'
                    sell_signals.append(signal_data)
                else:
                    signal_data['signal'] = '적정가 범위'
                    signal_data['icon'] = '🟡'
                    hold_signals.append(signal_data)
                    
            except ProperPrice.DoesNotExist:
                # 적정가격 없으면 계산
                self._calculate_proper_prices(stock)
        
        return Response({
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'hold_signals': hold_signals,
            'total': len(buy_signals) + len(sell_signals) + len(hold_signals),
        })

