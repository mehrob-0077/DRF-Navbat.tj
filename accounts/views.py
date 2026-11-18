import secrets
from datetime import timedelta
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from .serializers import RegisterSerializer

User = get_user_model()


def save_code(user, purpose):
    """Create and store a short-lived one-time code for the requested purpose."""
    code = f'{secrets.randbelow(1_000_000):06d}'
    setattr(user, f'{purpose}_code_hash', make_password(code))
    setattr(user, f'{purpose}_code_expires', timezone.now() + timedelta(minutes=30))
    user.save(update_fields=[f'{purpose}_code_hash', f'{purpose}_code_expires'])
    return code


def check_code(user, purpose, code):
    code_hash = getattr(user, f'{purpose}_code_hash', '')
    expires = getattr(user, f'{purpose}_code_expires', None)
    return bool(code_hash and expires and expires > timezone.now() and check_password(code, code_hash))


def clear_code(user, purpose):
    setattr(user, f'{purpose}_code_hash', '')
    setattr(user, f'{purpose}_code_expires', None)
    user.save(update_fields=[f'{purpose}_code_hash', f'{purpose}_code_expires'])


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    code = save_code(user, 'email_verification')
    send_mail(
        'Confirm your email',
        f'Your email verification code is {code}. It expires in 30 minutes.',
        None,
        [user.email],
        fail_silently=False,
    )
    return Response({'message': 'Registration successful. Check your email to verify your account.'}, status=status.HTTP_201_CREATED)
register_view.cls.throttle_scope = 'register'


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    if not email or not password:
        return Response({'message': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
    account = User.objects.filter(email__iexact=email).first()
    user = authenticate(request, username=account.username, password=password) if account else None
    if user is not None and user.is_email_verified:
        refresh = RefreshToken.for_user(user)
        return Response({'refresh': str(refresh), 'access': str(refresh.access_token)})
    return Response({'message': 'Username or password is incorrect, or email is not verified.'}, status=status.HTTP_401_UNAUTHORIZED)
login_view.cls.throttle_scope = 'login'


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    serializer = TokenRefreshSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
    except TokenError:
        return Response({'message': 'Refresh token is invalid or expired.'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.validated_data)


@api_view(['POST'])
def logout_view(request):
    token = request.data.get('refresh')
    if not token:
        return Response({'message': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        refresh = RefreshToken(token)
        if str(refresh['user_id']) != str(request.user.id):
            return Response({'message': 'This token belongs to another user.'}, status=status.HTTP_403_FORBIDDEN)
        refresh.blacklist()
    except TokenError:
        return Response({'message': 'Refresh token is invalid or expired.'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'Logout successful.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_view(request):
    email = request.data.get('email', '')
    user = User.objects.filter(email__iexact=email, is_active=True).first()
    code = request.data.get('code', '')
    if user is None or user.is_email_verified or not check_code(user, 'email_verification', code):
        return Response({'message': 'Verification code is invalid or expired.'}, status=status.HTTP_400_BAD_REQUEST)
    user.is_email_verified = True
    user.save(update_fields=['is_email_verified'])
    clear_code(user, 'email_verification')
    return Response({'message': 'Email verified successfully.'})
verify_email_view.cls.throttle_scope = 'email_verification'


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_view(request):
    email = request.data.get('email', '')
    user = User.objects.filter(email__iexact=email, is_active=True).first()
    if user:
        code = save_code(user, 'password_reset')
        send_mail(
            'Password reset',
            f'Your password reset code is {code}. It expires in 30 minutes.',
            None,
            [user.email],
            fail_silently=False,
        )
    return Response({'message': 'If an active account uses that email, password reset instructions have been sent.'})
password_reset_view.cls.throttle_scope = 'password_reset'


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm_view(request):
    email = request.data.get('email', '')
    user = User.objects.filter(email__iexact=email, is_active=True).first()
    code = request.data.get('code', '')
    if user is None or not check_code(user, 'password_reset', code):
        return Response({'message': 'Password reset code is invalid or expired.'}, status=status.HTTP_400_BAD_REQUEST)
    password = request.data.get('password', '')
    password2 = request.data.get('password2', '')
    if password != password2:
        return Response({'message': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        validate_password(password, user)
    except ValidationError as error:
        return Response({'message': list(error.messages)}, status=status.HTTP_400_BAD_REQUEST)
    user.set_password(password)
    user.save(update_fields=['password'])
    clear_code(user, 'password_reset')
    return Response({'message': 'Password reset successfully.'})
password_reset_confirm_view.cls.throttle_scope = 'password_reset_confirm'


@api_view(['POST'])
def change_password_view(request):
    old_password = request.data.get('old_password', '')
    password = request.data.get('password', '')
    password2 = request.data.get('password2', '')
    if not request.user.check_password(old_password):
        return Response({'message': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
    if password != password2:
        return Response({'message': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        validate_password(password, request.user)
    except ValidationError as error:
        return Response({'message': list(error.messages)}, status=status.HTTP_400_BAD_REQUEST)
    request.user.set_password(password)
    request.user.save(update_fields=['password'])
    return Response({'message': 'Password changed successfully.'})




