from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

from apps.portfolio.models import Portfolio, PortfolioSnapshot, HoldingSignal
from .serializers import (
    PortfolioListSerializer,
    PortfolioDetailSerializer,
    PortfolioCreateSerializer,
)

User = get_user_model()


class PortfolioViewSet(viewsets.ModelViewSet):
    """
    포트폴리오 관리 ViewSet
    """
    permission_classes = [AllowAny]  # 임시로 로그인 없이 사용 가능
    
    def get_queryset(self):
        """사용자 본인의 포트폴리오만 조회 (개발용: 임시 사용자)"""
        # 개발 환경: 임시 사용자 사용
        user = self.request.user if self.request.user.is_authenticated else self._get_dev_user()
        return Portfolio.objects.filter(user=user).select_related('stock').prefetch_related('signals', 'snapshot')
    
    def _get_dev_user(self):
        """개발용 임시 사용자 생성/조회"""
        user, created = User.objects.get_or_create(
            username='dev_user',
            defaults={
                'email': 'dev@newturn.com',
                'first_name': 'Dev',
                'last_name': 'User',
            }
        )
        return user
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PortfolioCreateSerializer
        elif self.action in ['retrieve', 'holding_decision']:
            return PortfolioDetailSerializer
        return PortfolioListSerializer
    
    def perform_create(self, serializer):
        """포트폴리오 생성 시 스냅샷도 함께 생성"""
        # 개발 환경: 임시 사용자 사용
        user = self.request.user if self.request.user.is_authenticated else self._get_dev_user()
        portfolio = serializer.save(user=user)
        
        # 매수 시점 스냅샷 생성 (TODO: 나중에 구현)
        # self.create_snapshot(portfolio)
        
        return portfolio
    
    def create_snapshot(self, portfolio):
        """매수 시점의 재무 지표 스냅샷 생성"""
        from api.stocks.views import StockViewSet
        
        # 현재 지표 계산
        stock_view = StockViewSet()
        indicators = stock_view.calculate_ttm_indicators(portfolio.stock)
        score = stock_view.calculate_score(indicators)
        
        # 스냅샷 생성
        PortfolioSnapshot.objects.create(
            portfolio=portfolio,
            snapshot_date=portfolio.purchase_date,
            fcf_margin=indicators.get('fcf_margin'),
            roe=indicators.get('roe'),
            debt_ratio=indicators.get('debt_ratio'),
            current_ratio=indicators.get('current_ratio'),
            revenue_growth=indicators.get('revenue_growth_yoy'),
            fcf_growth=indicators.get('fcf_growth_yoy'),
            total_score=score.get('total_score'),
            cashflow_score=score.get('cashflow_score'),
            safety_score=score.get('safety_score'),
            growth_score=score.get('growth_score'),
            raw_indicators=indicators,
        )
    
    @action(detail=True, methods=['get'])
    def holding_decision(self, request, pk=None):
        """
        보유 판단 분석
        """
        portfolio = self.get_object()
        
        # 현재 지표 계산
        from api.stocks.views import StockViewSet
        stock_view = StockViewSet()
        current_indicators = stock_view.calculate_ttm_indicators(portfolio.stock)
        current_score = stock_view.calculate_score(current_indicators)
        
        # 매수 시점 스냅샷
        snapshot = portfolio.snapshot
        if not snapshot:
            return Response({
                'error': '매수 시점 스냅샷이 없습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 변화 계산
        score_change = current_score['total_score'] - (snapshot.total_score or 0)
        fcf_margin_change = (current_indicators.get('fcf_margin', 0) or 0) - (snapshot.fcf_margin or 0)
        roe_change = (current_indicators.get('roe', 0) or 0) - (snapshot.roe or 0)
        debt_change = (current_indicators.get('debt_ratio', 0) or 0) - (snapshot.debt_ratio or 0)
        
        # FCF 추세 분석 (최근 4분기)
        fcf_trend = self.analyze_fcf_trend(portfolio.stock)
        
        # 경고 사항
        warnings = []
        if fcf_trend['consecutive_down'] >= 2:
            warnings.append(f"FCF {fcf_trend['consecutive_down']}분기 연속 감소")
        if abs(debt_change) > 20:  # 부채비율 20%p 이상 변화
            if debt_change > 0:
                warnings.append(f"부채비율 {debt_change:.1f}%p 증가")
            else:
                warnings.append(f"부채비율 {abs(debt_change):.1f}%p 감소 (개선)")
        if score_change < -15:
            warnings.append(f"점수 {abs(score_change)}점 하락")
        
        # 시그널 판단
        signal = self.determine_signal(score_change, fcf_trend, warnings, current_score['total_score'])
        
        # 판단 근거 생성
        recommendation = self.generate_recommendation(
            signal, score_change, fcf_trend, warnings,
            fcf_margin_change, roe_change, debt_change
        )
        
        # 시그널 저장
        HoldingSignal.objects.create(
            portfolio=portfolio,
            signal=signal,
            signal_date=datetime.now().date(),
            current_fcf_margin=current_indicators.get('fcf_margin'),
            current_roe=current_indicators.get('roe'),
            current_debt_ratio=current_indicators.get('debt_ratio'),
            current_score=current_score['total_score'],
            score_change=score_change,
            fcf_trend=fcf_trend.get('description'),
            warnings=warnings,
            recommendation=recommendation,
        )
        
        # 응답 데이터
        response_data = {
            'portfolio': PortfolioDetailSerializer(portfolio).data,
            'current_indicators': current_indicators,
            'current_score': current_score,
            'changes': {
                'score_change': score_change,
                'fcf_margin_change': fcf_margin_change,
                'roe_change': roe_change,
                'debt_change': debt_change,
            },
            'fcf_trend': fcf_trend,
            'signal': signal,
            'signal_display': dict(HoldingSignal.SIGNAL_CHOICES)[signal],
            'warnings': warnings,
            'recommendation': recommendation,
        }
        
        return Response(response_data)
    
    def analyze_fcf_trend(self, stock):
        """FCF 추세 분석 (최근 4분기)"""
        from apps.stocks.models import StockFinancialRaw
        
        recent_quarters = StockFinancialRaw.objects.filter(
            stock=stock
        ).order_by('-disclosure_year', '-disclosure_quarter')[:4]
        
        if len(recent_quarters) < 4:
            return {
                'consecutive_down': 0,
                'description': '데이터 부족',
                'trend': []
            }
        
        # 최신 순서대로
        fcf_values = [q.fcf for q in recent_quarters if q.fcf is not None]
        
        if len(fcf_values) < 4:
            return {
                'consecutive_down': 0,
                'description': '데이터 부족',
                'trend': []
            }
        
        # 연속 감소 분기 수
        consecutive_down = 0
        for i in range(len(fcf_values) - 1):
            if fcf_values[i] < fcf_values[i + 1]:
                consecutive_down += 1
            else:
                break
        
        # 추세 설명
        if consecutive_down == 0:
            if fcf_values[0] > fcf_values[1]:
                description = "최근 증가"
            else:
                description = "안정적"
        elif consecutive_down == 1:
            description = "1분기 감소"
        elif consecutive_down == 2:
            description = "2분기 연속 감소"
        else:
            description = f"{consecutive_down}분기 연속 감소"
        
        return {
            'consecutive_down': consecutive_down,
            'description': description,
            'trend': fcf_values,
        }
    
    def determine_signal(self, score_change, fcf_trend, warnings, current_score):
        """시그널 판단"""
        # 매도 고려
        if current_score < 60 or score_change < -20 or fcf_trend['consecutive_down'] >= 3:
            return 'CONSIDER_SELL'
        
        # 재검토 필요
        if score_change < -10 or fcf_trend['consecutive_down'] >= 2 or len(warnings) >= 2:
            return 'REVIEW'
        
        # 보유
        if score_change >= 0 and fcf_trend['consecutive_down'] == 0:
            return 'STRONG_HOLD'
        
        return 'HOLD'
    
    def generate_recommendation(self, signal, score_change, fcf_trend, warnings,
                                 fcf_margin_change, roe_change, debt_change):
        """판단 근거 생성"""
        parts = []
        
        # 점수 변화
        if score_change > 5:
            parts.append(f"점수 {score_change}점 상승으로 전반적으로 개선되었습니다.")
        elif score_change < -5:
            parts.append(f"점수 {abs(score_change)}점 하락으로 주의가 필요합니다.")
        else:
            parts.append("점수는 안정적입니다.")
        
        # FCF 추세
        if fcf_trend['consecutive_down'] == 0:
            parts.append("현금흐름은 안정적이거나 개선 중입니다.")
        elif fcf_trend['consecutive_down'] >= 2:
            parts.append(f"현금흐름이 {fcf_trend['consecutive_down']}분기 연속 감소하고 있어 주의가 필요합니다.")
        
        # 주요 지표 변화
        if fcf_margin_change > 2:
            parts.append(f"FCF Margin이 {fcf_margin_change:.1f}%p 개선되었습니다.")
        elif fcf_margin_change < -2:
            parts.append(f"FCF Margin이 {abs(fcf_margin_change):.1f}%p 악화되었습니다.")
        
        # 최종 판단
        if signal == 'STRONG_HOLD':
            parts.append("모든 지표가 양호하므로 계속 보유를 권장합니다.")
        elif signal == 'HOLD':
            parts.append("전반적으로 안정적이나 지속적인 모니터링이 필요합니다.")
        elif signal == 'REVIEW':
            parts.append("일부 지표가 악화되어 재검토가 필요합니다.")
        else:  # CONSIDER_SELL
            parts.append("여러 지표가 악화되어 매도를 고려해볼 시점입니다.")
        
        return " ".join(parts)

