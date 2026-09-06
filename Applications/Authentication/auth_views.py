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
       serializer = self.serializer_class(data=request.data)
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
       serializer = self.serializer_class(data=request.data, context={'request': request})
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
        serializer = self.serializer_class(data=request.data)
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


@method_decorator(rate_limit(key='ip', rate='3/m', block=True), name='post')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("identifier")
        password = request.data.get("password")


        if not identifier or not password:
            return Response(
                {"message": "Identifier and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(
            Q(username=identifier) | Q(email=identifier) | Q(phone=identifier)
        ).first()

        if not user or not user.check_password(password):
            return Response(
                {"message": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        response = Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data
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

        valid_pins = ['7890', 'ILA2026']
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
        franchises = FranchisePartner.objects.all().order_by('-created_at')
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
        logs = AuditLog.objects.all().order_by('-timestamp')[:100]
        return Response(AuditLogSerializer(logs, many=True).data)

