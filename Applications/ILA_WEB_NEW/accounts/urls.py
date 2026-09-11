from django.urls import path
from .views import (
    LoginView,
    RegisterView,
    CurrentUserView,
    ChangePasswordView,
    CreateStaffUserView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='auth_login'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('me/', CurrentUserView.as_view(), name='auth_me'),
    path('change-password/', ChangePasswordView.as_view(), name='auth_change_password'),
    path('create-staff/', CreateStaffUserView.as_view(), name='auth_create_staff'),
]
