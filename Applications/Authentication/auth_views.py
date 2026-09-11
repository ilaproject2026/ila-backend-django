from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.db.models import Q
from django.utils.decorators import method_decorator
from django_smart_ratelimit import rate_limit
from .auth_models import User
from .auth_serializers import (
    LoginSerializer,
    UserRegistrationSerializer,
    ResentOTPSerializer,
    EmailOTPVerifySerializer,
    UserSerializer,
)
from .auth_utils import (
    set_auth_cookies,
    set_access_cookie,
    delete_auth_cookies,
)



@method_decorator(rate_limit(key='ip', rate='3/m', block=True), name='post')
class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        payload = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if not payload.get('identifier'):
            payload['identifier'] = payload.get('email') or payload.get('phone')
        serializer = self.serializer_class(data=payload)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "One time password sent to your email/phone for verification"}, status=status.HTTP_201_CREATED)
        return Response({
            'message': 'Registration failed',
            'errors': serializer.errors
          }, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(rate_limit(key='ip', rate='2/m', block=True), name='post')
class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ResentOTPSerializer

    def post(self, request):
        payload = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if not payload.get('identifier'):
            payload['identifier'] = payload.get('email') or payload.get('phone')
        serializer = self.serializer_class(data=payload, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "One time password sent to your email/phone for verification"}, status=status.HTTP_201_CREATED)
        return Response({
            'message': 'Registration failed',
            'errors': serializer.errors
          }, status=status.HTTP_400_BAD_REQUEST)
   
   
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    serializer_class = EmailOTPVerifySerializer

    def post(self, request):
        payload = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if not payload.get('identifier'):
            payload['identifier'] = payload.get('email') or payload.get('phone')
        serializer = self.serializer_class(data=payload)
        if serializer.is_valid():
            user = serializer.save()  # capture the created user here
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = Response({
                'message': 'Account verified successfully',
            }, status=status.HTTP_200_OK)

            set_auth_cookies(response, refresh)
            return response
        # --- flatten the error response here ---
        errors = serializer.errors
        message = None

        if isinstance(errors, dict):
            # Try to get first field error
            for key, value in errors.items():
                if isinstance(value, list) and len(value) > 0:
                    message = value[0]
                else:
                    message = value
                break
        elif isinstance(errors, list):
            message = errors[0]
        else:
            message = str(errors)

        return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(rate_limit(key='ip', rate='60/m', block=True), name='post')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            detail_msg = "Invalid credentials. Please verify your password."
            errors = serializer.errors
            if isinstance(errors, dict) and 'detail' in errors:
                d = errors['detail']
                detail_msg = d[0] if isinstance(d, list) and d else str(d)
            elif isinstance(errors, dict):
                first_key = next(iter(errors))
                val = errors[first_key]
                detail_msg = val[0] if isinstance(val, list) and val else str(val)
            elif isinstance(errors, list) and errors:
                detail_msg = str(errors[0])

            return Response({"detail": detail_msg}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "fullname": getattr(user, 'full_name', None) or user.fullname or user.get_full_name() or user.username,
            "role": user.role,
            "department": user.department or ("Super Admin" if user.is_superuser else "General"),
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "is_email_verified": getattr(user, 'is_email_verified', True),
        }

        response = Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": user_data,
            "message": "Login successful"
        }, status=status.HTTP_200_OK)

        # Set cookies
        set_auth_cookies(response, refresh)
        return response
    
class LogoutView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):

        response = Response({
            "message": "Logged out successfully"
        }, status=status.HTTP_200_OK)

        delete_auth_cookies(response)
        return response

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        refresh_token = request.data.get("refresh") or request.COOKIES.get("refresh_token")

        if not refresh_token:
            raise AuthenticationFailed("Authentication credentials were not provided")

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
        except Exception:
            raise AuthenticationFailed("Invalid refresh token")

        response = Response({
            "message": "Access token refreshed",
            "access": new_access_token,
        }, status=status.HTTP_200_OK)
        set_access_cookie(response, new_access_token)
        return response

class CheckLoginView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response({
                'is_logged_in': False,
            }, status=status.HTTP_200_OK)
            
        return Response({
            'is_logged_in': True,
            'user': UserSerializer(request.user).data
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """Returns the current authenticated user profile & permissions"""
    def get(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)


class SecurityGateVerifyView(APIView):
    """
    Validates Level 1 Edit PIN ('7890' / 'ILA2026' or user's security_pin_hash).
    Returns elevated status and verification token for high-privilege operations.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        pin = request.data.get('pin') or request.data.get('authCode')
        if not pin:
            return Response({'error': 'PIN code is required'}, status=status.HTTP_400_BAD_REQUEST)

        from django.conf import settings as django_settings
        from decouple import config as dtconfig
        # Read security PINs from environment (comma-separated), fallback to defaults for dev
        raw_pins = dtconfig('SECURITY_GATE_PINS', default='7890,ILA2026')
        valid_pins = [p.strip() for p in raw_pins.split(',') if p.strip()]
        user = request.user if request.user and request.user.is_authenticated else None
        
        # Check global override PINs or user specific pin
        is_valid = (str(pin).strip() in valid_pins)
        if not is_valid and user and user.security_pin_hash:
            from django.contrib.auth.hashers import check_password
            if check_password(str(pin).strip(), user.security_pin_hash):
                is_valid = True

        if is_valid:
            import hmac, hashlib, time
            from django.conf import settings
            token_payload = f"{user.id if user else 'anonymous'}:{int(time.time()) + 900}"
            elevated_token = hmac.new(settings.SECRET_KEY.encode(), token_payload.encode(), hashlib.sha256).hexdigest()
            return Response({
                'valid': True,
                'message': 'Security Gate unlocked successfully',
                'elevated_token': elevated_token,
                'expires_in': 900
            }, status=status.HTTP_200_OK)

        return Response({
            'valid': False,
            'error': 'Invalid Security Gate PIN'
        }, status=status.HTTP_403_FORBIDDEN)


class FranchisePartnerListCreateView(APIView):
    def get(self, request):
        from .auth_models import FranchisePartner
        from .auth_serializers import FranchisePartnerSerializer
        franchises = FranchisePartner.objects.select_related('created_by').all().order_by('-created_at')
        return Response(FranchisePartnerSerializer(franchises, many=True).data)

    def post(self, request):
        from .auth_models import FranchisePartner
        from .auth_serializers import FranchisePartnerSerializer
        serializer = FranchisePartnerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user if request.user.is_authenticated else None)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuditLogListView(APIView):
    def get(self, request):
        from .auth_models import AuditLog
        from .auth_serializers import AuditLogSerializer
        logs = AuditLog.objects.select_related('user').all().order_by('-timestamp')[:100]
        return Response(AuditLogSerializer(logs, many=True).data)

