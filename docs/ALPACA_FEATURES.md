# 📊 Alpaca API 기능 및 서비스 화면 구현 가능 여부

**작성일**: 2024.11.07  
**목적**: Alpaca API로 실제 서비스 화면에서 구현 가능한 기능 정리

---

## ✅ **구현 가능한 기능 목록**

### **1. 주식 매수/매도** ✅
- ✅ **시장가 주문** (Market Order)
- ✅ **지정가 주문** (Limit Order)
- ✅ **정지가 주문** (Stop Order)
- ✅ **정지 지정가 주문** (Stop Limit Order)
- ✅ **주문 취소**
- ✅ **주문 상태 조회**

### **2. 보유 종목 조회** ✅
- ✅ **전체 보유 포지션 조회**
- ✅ **특정 종목 보유 수량 조회**
- ✅ **평균 매수가 조회**
- ✅ **현재 가치 조회**
- ✅ **수익/손실 계산**

### **3. 계좌 정보** ✅
- ✅ **계좌 잔액 조회** (현금)
- ✅ **총 자산 조회** (현금 + 주식)
- ✅ **구매력 조회** (Buying Power)
- ✅ **계좌 상태 조회**

### **4. 주가 데이터** ✅
- ✅ **실시간 주가 조회** (Quote)
- ✅ **과거 주가 조회** (Historical Data)
- ✅ **일봉/분봉 데이터**
- ✅ **거래량 조회**

### **5. 주문 내역** ✅
- ✅ **주문 내역 조회**
- ✅ **체결 내역 조회**
- ✅ **미체결 주문 조회**

---

## 🎨 **서비스 화면 구현 예시**

### **1. 보유 종목 대시보드**

```typescript
// 프론트엔드 컴포넌트 예시

interface Position {
  symbol: string
  qty: number
  avg_entry_price: number
  current_price: number
  market_value: number
  unrealized_pl: number  // 미실현 손익
  unrealized_plpc: number  // 미실현 손익률 (%)
}

// API 호출
const positions = await fetch('/api/alpaca/positions/')
```

**화면 구성:**
```
┌─────────────────────────────────────┐
│  내 보유 종목                       │
├─────────────────────────────────────┤
│  NVDA                               │
│  보유: 5주                          │
│  평균 매수가: $500                  │
│  현재가: $583.33                    │
│  현재 가치: $2,916.65               │
│  수익: +$416.65 (+16.7%) ✅         │
│  [매도하기]                         │
├─────────────────────────────────────┤
│  MSFT                               │
│  보유: 10주                         │
│  평균 매수가: $400                  │
│  현재가: $380                       │
│  현재 가치: $3,800                  │
│  손실: -$200 (-5.0%) ⏸️            │
│  [보유 중]                          │
└─────────────────────────────────────┘
```

### **2. 주식 매수 화면**

```typescript
// 매수 주문
const buyOrder = await fetch('/api/alpaca/orders/', {
  method: 'POST',
  body: JSON.stringify({
    symbol: 'NVDA',
    qty: 1,
    side: 'buy',
    type: 'market',  // 또는 'limit'
    time_in_force: 'day'
  })
})
```

**화면 구성:**
```
┌─────────────────────────────────────┐
│  NVDA 매수                          │
├─────────────────────────────────────┤
│  현재가: $583.33                    │
│  매수 주수: [1] 주                  │
│  예상 금액: $583.33                 │
│  수수료: $0 (무료)                  │
│  총 금액: $583.33                   │
│                                     │
│  주문 유형:                         │
│  ○ 시장가                          │
│  ● 지정가                          │
│  지정가: [$583.33]                  │
│                                     │
│  [매수하기]                         │
└─────────────────────────────────────┘
```

### **3. 주식 매도 화면**

```typescript
// 매도 주문
const sellOrder = await fetch('/api/alpaca/orders/', {
  method: 'POST',
  body: JSON.stringify({
    symbol: 'NVDA',
    qty: 5,
    side: 'sell',
    type: 'market'
  })
})
```

**화면 구성:**
```
┌─────────────────────────────────────┐
│  NVDA 매도                          │
├─────────────────────────────────────┤
│  보유 주수: 5주                     │
│  매도 주수: [5] 주                  │
│  평균 매수가: $500                  │
│  현재가: $583.33                    │
│  예상 수익: $416.65 (+16.7%)        │
│  수수료: $0 (무료)                  │
│  예상 수령액: $2,916.65             │
│                                     │
│  [매도하기]                         │
└─────────────────────────────────────┘
```

### **4. 계좌 현황 화면**

```typescript
// 계좌 정보 조회
const account = await fetch('/api/alpaca/account/')
```

**화면 구성:**
```
┌─────────────────────────────────────┐
│  계좌 현황                          │
├─────────────────────────────────────┤
│  현금 잔액: $10,000                 │
│  주식 가치: $6,716.65               │
│  총 자산: $16,716.65                │
│  구매력: $20,000                    │
│                                     │
│  오늘 수익: +$216.65 (+1.3%)        │
│  총 수익: +$416.65 (+2.6%)          │
└─────────────────────────────────────┘
```

### **5. 주문 내역 화면**

```typescript
// 주문 내역 조회
const orders = await fetch('/api/alpaca/orders/?status=all')
```

**화면 구성:**
```
┌─────────────────────────────────────┐
│  주문 내역                          │
├─────────────────────────────────────┤
│  NVDA 매수 5주                      │
│  2024-11-07 10:30 AM               │
│  시장가 $500                        │
│  상태: 체결 완료 ✅                 │
├─────────────────────────────────────┤
│  MSFT 매도 10주                     │
│  2024-11-06 2:15 PM                │
│  지정가 $400                        │
│  상태: 체결 완료 ✅                 │
└─────────────────────────────────────┘
```

---

## 🔧 **백엔드 API 구현**

### **1. Alpaca API 래퍼 확장**

```python
# apps/broker/alpaca_api.py

class AlpacaAPI:
    # ... 기존 코드 ...
    
    def get_positions(self) -> list:
        """보유 포지션 조회"""
        positions = self.trading_client.get_all_positions()
        return [
            {
                'symbol': pos.symbol,
                'qty': float(pos.qty),
                'avg_entry_price': float(pos.avg_entry_price),
                'current_price': float(pos.current_price),
                'market_value': float(pos.market_value),
                'unrealized_pl': float(pos.unrealized_pl),  # 미실현 손익
                'unrealized_plpc': float(pos.unrealized_plpc),  # 미실현 손익률 (%)
                'side': pos.side.value,
            }
            for pos in positions
        ]
    
    def get_position(self, symbol: str) -> dict:
        """특정 종목 보유 포지션 조회"""
        try:
            position = self.trading_client.get_open_position(symbol)
            return {
                'symbol': position.symbol,
                'qty': float(position.qty),
                'avg_entry_price': float(position.avg_entry_price),
                'current_price': float(position.current_price),
                'market_value': float(position.market_value),
                'unrealized_pl': float(position.unrealized_pl),
                'unrealized_plpc': float(position.unrealized_plpc),
            }
        except Exception:
            return None  # 보유하지 않은 종목
    
    def get_account(self) -> dict:
        """계좌 정보 조회"""
        account = self.trading_client.get_account()
        return {
            'account_number': account.account_number,
            'cash': float(account.cash),
            'portfolio_value': float(account.portfolio_value),  # 총 자산
            'buying_power': float(account.buying_power),  # 구매력
            'equity': float(account.equity),  # 자본
            'day_trading_buying_power': float(account.day_trading_buying_power),
            'pattern_day_trader': account.pattern_day_trader,
            'trading_blocked': account.trading_blocked,
            'account_blocked': account.account_blocked,
            'status': account.status.value,
        }
    
    def get_orders(self, status: str = 'all', limit: int = 50) -> list:
        """
        주문 내역 조회
        
        Args:
            status: 'all', 'open', 'closed'
            limit: 최대 조회 개수
        """
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
                'id': str(order.id),
                'symbol': order.symbol,
                'qty': float(order.qty),
                'filled_qty': float(order.filled_qty or 0),
                'side': order.side.value,  # 'buy' or 'sell'
                'order_type': order.order_type.value,  # 'market', 'limit', etc.
                'status': order.status.value,  # 'new', 'filled', 'canceled', etc.
                'limit_price': float(order.limit_price) if order.limit_price else None,
                'stop_price': float(order.stop_price) if order.stop_price else None,
                'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else None,
                'submitted_at': order.submitted_at.isoformat() if order.submitted_at else None,
                'filled_at': order.filled_at.isoformat() if order.filled_at else None,
            }
            for order in orders
        ]
    
    def cancel_order(self, order_id: str) -> bool:
        """주문 취소"""
        try:
            self.trading_client.cancel_order_by_id(order_id)
            return True
        except Exception:
            return False
    
    def get_order(self, order_id: str) -> dict:
        """특정 주문 조회"""
        order = self.trading_client.get_order_by_id(order_id)
        return {
            'id': str(order.id),
            'symbol': order.symbol,
            'qty': float(order.qty),
            'filled_qty': float(order.filled_qty or 0),
            'side': order.side.value,
            'order_type': order.order_type.value,
            'status': order.status.value,
            'limit_price': float(order.limit_price) if order.limit_price else None,
            'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else None,
        }
```

---

### **2. Django REST API 엔드포인트**

```python
# api/alpaca/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.broker.alpaca_api import AlpacaAPI

class AlpacaTradingViewSet(viewsets.ViewSet):
    """Alpaca 주식 매매 API"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alpaca = AlpacaAPI(paper=False)  # Live Trading
    
    @action(detail=False, methods=['get'])
    def account(self, request):
        """계좌 정보 조회"""
        try:
            account_info = self.alpaca.get_account()
            return Response(account_info)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def positions(self, request):
        """보유 포지션 조회"""
        try:
            positions = self.alpaca.get_positions()
            return Response({'positions': positions})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='positions/(?P<symbol>[^/.]+)')
    def position(self, request, symbol=None):
        """특정 종목 보유 포지션 조회"""
        try:
            position = self.alpaca.get_position(symbol.upper())
            if position:
                return Response(position)
            else:
                return Response(
                    {'error': '보유하지 않은 종목입니다.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def buy(self, request):
        """주식 매수"""
        symbol = request.data.get('symbol')
        qty = request.data.get('qty')
        order_type = request.data.get('order_type', 'market')
        limit_price = request.data.get('limit_price')
        
        if not symbol or not qty:
            return Response(
                {'error': 'symbol과 qty가 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = self.alpaca.buy_stock(
                symbol=symbol.upper(),
                quantity=int(qty),
                order_type=order_type
            )
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def sell(self, request):
        """주식 매도"""
        symbol = request.data.get('symbol')
        qty = request.data.get('qty')
        order_type = request.data.get('order_type', 'market')
        
        if not symbol or not qty:
            return Response(
                {'error': 'symbol과 qty가 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = self.alpaca.sell_stock(
                symbol=symbol.upper(),
                quantity=int(qty),
                order_type=order_type
            )
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def orders(self, request):
        """주문 내역 조회"""
        status_param = request.query_params.get('status', 'all')
        limit = int(request.query_params.get('limit', 50))
        
        try:
            orders = self.alpaca.get_orders(status=status_param, limit=limit)
            return Response({'orders': orders})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='orders/(?P<order_id>[^/.]+)')
    def order(self, request, order_id=None):
        """특정 주문 조회"""
        try:
            order = self.alpaca.get_order(order_id)
            return Response(order)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'], url_path='orders/(?P<order_id>[^/.]+)/cancel')
    def cancel_order(self, request, order_id=None):
        """주문 취소"""
        try:
            success = self.alpaca.cancel_order(order_id)
            if success:
                return Response({'success': True})
            else:
                return Response(
                    {'error': '주문 취소 실패'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
```

---

### **3. URL 설정**

```python
# api/alpaca/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlpacaTradingViewSet

router = DefaultRouter()
router.register(r'trading', AlpacaTradingViewSet, basename='alpaca-trading')

urlpatterns = [
    path('', include(router.urls)),
]
```

```python
# newturn/urls.py

urlpatterns = [
    # ... 기존 URL ...
    path('api/alpaca/', include('api.alpaca.urls')),
]
```

---

## 📱 **프론트엔드 API 클라이언트**

```typescript
// apps/investor/src/lib/api/alpaca.ts

import { apiClient } from '../axios'

export interface Position {
  symbol: string
  qty: number
  avg_entry_price: number
  current_price: number
  market_value: number
  unrealized_pl: number
  unrealized_plpc: number
}

export interface Account {
  cash: number
  portfolio_value: number
  buying_power: number
  equity: number
  status: string
}

export interface Order {
  id: string
  symbol: string
  qty: number
  filled_qty: number
  side: 'buy' | 'sell'
  order_type: string
  status: string
  filled_avg_price?: number
  submitted_at?: string
}

// 계좌 정보 조회
export async function getAccount(): Promise<Account> {
  const { data } = await apiClient.get('/api/alpaca/trading/account/')
  return data
}

// 보유 포지션 조회
export async function getPositions(): Promise<Position[]> {
  const { data } = await apiClient.get('/api/alpaca/trading/positions/')
  return data.positions
}

// 특정 종목 보유 포지션 조회
export async function getPosition(symbol: string): Promise<Position | null> {
  try {
    const { data } = await apiClient.get(`/api/alpaca/trading/positions/${symbol}/`)
    return data
  } catch (error) {
    return null
  }
}

// 주식 매수
export async function buyStock(params: {
  symbol: string
  qty: number
  order_type?: 'market' | 'limit'
  limit_price?: number
}): Promise<Order> {
  const { data } = await apiClient.post('/api/alpaca/trading/buy/', params)
  return data
}

// 주식 매도
export async function sellStock(params: {
  symbol: string
  qty: number
  order_type?: 'market' | 'limit'
}): Promise<Order> {
  const { data } = await apiClient.post('/api/alpaca/trading/sell/', params)
  return data
}

// 주문 내역 조회
export async function getOrders(params?: {
  status?: 'all' | 'open' | 'closed'
  limit?: number
}): Promise<Order[]> {
  const { data } = await apiClient.get('/api/alpaca/trading/orders/', { params })
  return data.orders
}

// 주문 취소
export async function cancelOrder(orderId: string): Promise<void> {
  await apiClient.post(`/api/alpaca/trading/orders/${orderId}/cancel/`)
}
```

---

## 🎯 **실제 사용 시나리오**

### **시나리오 1: 보유 종목 확인**

```
사용자: "내가 보유한 종목 보기" 클릭
  ↓
프론트엔드: GET /api/alpaca/trading/positions/
  ↓
백엔드: Alpaca API 호출
  → positions = alpaca.get_positions()
  ↓
응답: [
  {symbol: 'NVDA', qty: 5, current_price: 583.33, ...},
  {symbol: 'MSFT', qty: 10, current_price: 380, ...}
]
  ↓
프론트엔드: 보유 종목 리스트 표시
```

### **시나리오 2: 주식 매수**

```
사용자: "NVDA 1주 매수" 클릭
  ↓
프론트엔드: POST /api/alpaca/trading/buy/
  {symbol: 'NVDA', qty: 1, order_type: 'market'}
  ↓
백엔드: Alpaca API 호출
  → order = alpaca.buy_stock('NVDA', 1, 'market')
  ↓
응답: {
  order_id: 'xxx',
  status: 'filled',
  filled_qty: 1,
  filled_avg_price: 583.33
}
  ↓
프론트엔드: "매수 완료!" 메시지 표시
```

### **시나리오 3: 주식 매도**

```
사용자: "NVDA 5주 매도" 클릭
  ↓
프론트엔드: POST /api/alpaca/trading/sell/
  {symbol: 'NVDA', qty: 5, order_type: 'market'}
  ↓
백엔드: Alpaca API 호출
  → order = alpaca.sell_stock('NVDA', 5, 'market')
  ↓
응답: {
  order_id: 'yyy',
  status: 'filled',
  filled_qty: 5,
  filled_avg_price: 583.33
}
  ↓
프론트엔드: "매도 완료! 수익: +$416.65" 메시지 표시
```

---

## ⚠️ **주의사항**

### **1. Paper Trading vs Live Trading**
- **Paper Trading**: 가상 자금으로 테스트 (무료)
- **Live Trading**: 실제 돈으로 거래 (신중!)
- 초기에는 Paper Trading으로 충분히 테스트

### **2. 주문 제한**
- **최소 주문 금액**: $1
- **최소 주문 수량**: 1주 (정수만 가능, 소수점 불가)
- **시장 시간**: 미국 증시 개장 시간 (EST 9:30 AM - 4:00 PM)

### **3. Rate Limit**
- Alpaca API는 Rate Limit이 있음
- 초당 요청 수 제한 확인 필요
- 너무 빈번한 요청은 피하기

### **4. 에러 처리**
- 주문 실패 시 에러 메시지 표시
- 계좌 잔액 부족 시 알림
- 시장 시간 외 주문 시 안내

---

## ✅ **결론**

**Alpaca API로 다음 기능들이 모두 구현 가능합니다:**

1. ✅ **주식 매수/매도** - 시장가, 지정가 모두 가능
2. ✅ **보유 종목 조회** - 실시간 포지션 및 수익/손실
3. ✅ **계좌 정보** - 잔액, 총 자산, 구매력
4. ✅ **주문 내역** - 주문 조회, 취소
5. ✅ **주가 조회** - 실시간 주가, 과거 데이터

**실제 서비스 화면에서 완전히 구현 가능합니다!** 🎉

---

**작성자**: AI Assistant  
**업데이트**: 2024.11.07

