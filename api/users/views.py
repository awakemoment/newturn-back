"""
사용자 인증 API
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def kakao_login(request):
    """
    카카오 로그인
    POST /api/users/kakao/login/
    Body: { "access_token": "카카오 액세스 토큰" }
    """
    access_token = request.data.get('access_token')
    
    if not access_token:
        return Response(
            {'error': '액세스 토큰이 필요합니다'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # TODO: 카카오 API로 사용자 정보 조회
    # 현재는 임시로 개발용 사용자 반환
    user, created = User.objects.get_or_create(
        username='kakao_dev_user',
        defaults={
            'email': 'kakao@newturn.com',
            'first_name': '카카오',
            'last_name': '사용자',
        }
    )
    
    # 토큰 생성
    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
        'is_new_user': created,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    """
    구글 로그인
    POST /api/users/google/login/
    Body: { "access_token": "구글 액세스 토큰" }
    """
    access_token = request.data.get('access_token')
    
    if not access_token:
        return Response(
            {'error': '액세스 토큰이 필요합니다'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # TODO: 구글 API로 사용자 정보 조회
    # 현재는 임시로 개발용 사용자 반환
    user, created = User.objects.get_or_create(
        username='google_dev_user',
        defaults={
            'email': 'google@newturn.com',
            'first_name': '구글',
            'last_name': '사용자',
        }
    )
    
    # 토큰 생성
    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
        'is_new_user': created,
    })


@api_view(['POST'])
def logout(request):
    """
    로그아웃
    POST /api/users/logout/
    """
    if request.user.is_authenticated:
        # 토큰 삭제
        try:
            request.user.auth_token.delete()
        except Exception:
            pass
    
    return Response({'message': '로그아웃되었습니다'})


@api_view(['GET'])
def me(request):
    """
    현재 사용자 정보
    GET /api/users/me/
    """
    if not request.user.is_authenticated:
        return Response(
            {'error': '인증이 필요합니다'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
    })

