from django.urls import path
from .auth_views import (
    RegisterView,
    ResendOTPView,
    VerifyOTPView,
    LoginView,
    LogoutView,
    RefreshTokenView,
    CheckLoginView,
    UserProfileView,
    SecurityGateVerifyView,
    FranchisePartnerListCreateView,
    AuditLogListView,
)


urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('resend-otp/', ResendOTPView.as_view(), name='resent-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token-refresh'),
    path('check-login/', CheckLoginView.as_view(), name='check-login'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('verify-security-gate/', SecurityGateVerifyView.as_view(), name='verify-security-gate'),
    path('franchise/', FranchisePartnerListCreateView.as_view(), name='franchise-list-create'),
    path('franchise/create/', FranchisePartnerListCreateView.as_view(), name='franchise-create'),
    path('audit-logs/', AuditLogListView.as_view(), name='audit-logs-list'),
]
