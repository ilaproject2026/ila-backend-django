from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import (
    UserSerializer,
    LoginSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    StaffUserSerializer,
)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user).data

        return Response({
            'token': token.key,
            'user': user_data,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            error_msg = next(iter(serializer.errors.values()))
            if isinstance(error_msg, list):
                error_msg = error_msg[0]
            return Response({'error': str(error_msg), 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user).data

        return Response({
            'token': token.key,
            'user': user_data,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)


class CurrentUserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            return Response({'user': UserSerializer(request.user).data})
        return Response({'user': None, 'authenticated': False})


class ChangePasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        new_password = request.data.get('new_password', '').strip()

        if not new_password or len(new_password) < 6:
            return Response({'error': 'New password must be at least 6 characters long.'}, status=status.HTTP_400_BAD_REQUEST)

        user = None
        if request.user.is_authenticated:
            user = request.user
        elif email:
            user = User.objects.filter(email__iexact=email).first()

        if not user:
            return Response({'error': 'User not found or unauthenticated.'}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()

        # Refresh token
        Token.objects.filter(user=user).delete()
        new_token = Token.objects.create(user=user)

        return Response({
            'message': 'Password updated successfully.',
            'token': new_token.key
        }, status=status.HTTP_200_OK)


class CreateStaffUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', 'ILA@staff2026')
        department = request.data.get('department', 'Academic Counselor')
        role = request.data.get('role', 'team')
        staff_id = request.data.get('staff_id', '').strip()
        scope = request.data.get('scope', 'all')
        phone = request.data.get('phone', '')

        if not name or not email:
            return Response({'error': 'Name and Email are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email__iexact=email).exists():
            return Response({'error': 'A staff member with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        name_parts = name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        username = staff_id.lower() if staff_id else email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=True
        )

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.department = department
        profile.staff_id = staff_id
        profile.scope = scope
        profile.phone = phone
        profile.save()

        return Response({
            'message': f'Staff user {name} provisioned successfully.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
