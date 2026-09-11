from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role', 'department', 'staff_id', 'scope', 'phone', 'avatar_url', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'is_staff', 'is_superuser', 'profile']

    def get_full_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else obj.username


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True, help_text="Email, Username, or Staff ID")
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        identifier = data.get('identifier', '').strip()
        password = data.get('password', '')

        if not identifier or not password:
            raise serializers.ValidationError("Both identifier and password are required.")

        # Try authenticate by username
        user = authenticate(username=identifier, password=password)

        # If not authenticated, try by email
        if user is None and '@' in identifier:
            try:
                user_obj = User.objects.get(email__iexact=identifier)
                user = authenticate(username=user_obj.username, password=password)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                user = None

        # If not authenticated, try by staff_id
        if user is None:
            try:
                profile = UserProfile.objects.filter(staff_id__iexact=identifier).first()
                if profile:
                    user = authenticate(username=profile.user.username, password=password)
            except Exception:
                user = None

        if user is None:
            raise serializers.ValidationError("Invalid credentials. Please check your username/email and password.")

        if not user.is_active:
            raise serializers.ValidationError("This user account is inactive.")

        data['user'] = user
        return data


class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=200, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=6, write_only=True, required=True)
    role = serializers.CharField(max_length=50, default='student', required=False)
    department = serializers.CharField(max_length=100, required=False, default='Student')
    phone = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email address already exists.")
        return value.lower()

    def create(self, validated_data):
        full_name = validated_data.get('full_name', '').strip()
        email = validated_data.get('email', '').strip().lower()
        password = validated_data.get('password')
        role = 'student'
        department = 'Student'
        phone = validated_data.get('phone', '')

        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        username = email.split('@')[0]
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
            last_name=last_name
        )

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.department = department
        profile.phone = phone
        profile.save()

        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=False, allow_blank=True)
    new_password = serializers.CharField(min_length=6, required=True)

    def validate_new_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters.")
        return value


class StaffUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='get_full_name', read_only=True)
    role = serializers.CharField(source='profile.role', read_only=True)
    department = serializers.CharField(source='profile.department', read_only=True)
    staff_id = serializers.CharField(source='profile.staff_id', read_only=True)
    scope = serializers.CharField(source='profile.scope', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'role', 'department', 'staff_id', 'scope', 'is_active']
