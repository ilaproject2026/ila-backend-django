from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

User = get_user_model()

def get_user_from_request(request):

    access_token = None

    # 1️⃣ Check Authorization header (Bearer <token>)
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        access_token = auth_header.split(' ')[1]

    # 2️⃣ Fallback: check cookie
    if not access_token:
        access_token = request.COOKIES.get('access_token')

    # 3️⃣ If still not found
    if not access_token:
        raise AuthenticationFailed("No access token provided.")

    # 4️⃣ Validate token
    try:
        token = AccessToken(access_token)
        user_id = token['user_id']
        user = User.objects.get(id=user_id)
        return user
    except Exception as e:
        raise AuthenticationFailed(f"Invalid or expired token: {str(e)}")


def set_auth_cookies(response, refresh):
    secure = getattr(settings, 'SIMPLE_JWT_COOKIE_SECURE', False)
    samesite = getattr(settings, 'SIMPLE_JWT_COOKIE_SAMESITE', 'Lax')
    httponly = getattr(settings, 'SIMPLE_JWT_COOKIE_HTTPONLY', True)
    
    response.set_cookie(
        "access_token",
        str(refresh.access_token),
        httponly=httponly,
        secure=secure,
        samesite=samesite,
        path="/",
        max_age=360000
    )
    response.set_cookie(
        "refresh_token",
        str(refresh),
        httponly=httponly,
        secure=secure,
        samesite=samesite,
        path="/",
        max_age=7 * 24 * 360000
    )

def set_access_cookie(response, access_token):
    secure = getattr(settings, 'SIMPLE_JWT_COOKIE_SECURE', False)
    samesite = getattr(settings, 'SIMPLE_JWT_COOKIE_SAMESITE', 'Lax')
    httponly = getattr(settings, 'SIMPLE_JWT_COOKIE_HTTPONLY', True)
    
    response.set_cookie(
        "access_token",
        str(access_token),
        httponly=httponly,
        secure=secure,
        samesite=samesite,
        path="/",
        max_age=360000
    )

def delete_auth_cookies(response):
    samesite = getattr(settings, 'SIMPLE_JWT_COOKIE_SAMESITE', 'Lax')
    
    response.delete_cookie("access_token", path="/", samesite=samesite)
    response.delete_cookie("refresh_token", path="/", samesite=samesite)