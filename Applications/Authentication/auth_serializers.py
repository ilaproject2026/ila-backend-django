import re
import random
from rest_framework import serializers

from .auth_models import User, RegistrationOTP
from .auth_emails import send_registration_otp_email


# --------------------------------------------- Authentication Serializers -------------------------------------------------------------

class UserRegistrationSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    referral_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_identifier(self, value):
        value = value.strip()
        is_email = bool(re.match(r"[^@]+@[^@]+\.[^@]+", value))
        is_phone = bool(value.isdigit() and len(value) >= 7)

        if not (is_email or is_phone):
            raise serializers.ValidationError("Must be a valid email address or phone number")

        if is_email and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists")

        if is_phone and User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("An account with this phone number already exists")

        return value

    def validate_username(self, value):
        value = value.strip()
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken")
        return value

    def validate_referral_code(self, value):
        if value:
            value = value.strip()
            if not User.objects.filter(referral_code=value, is_active=True).exists():
                raise serializers.ValidationError("Invalid referral code")
        return value

    def validate(self, data):
        referral_code = data.get("referral_code")
        identifier = data.get("identifier")
        username = data.get("username")

        if referral_code:
            referrer = User.objects.filter(referral_code=referral_code, is_active=True).first()
            if referrer and (referrer.username == username or referrer.email == identifier or referrer.phone == identifier):
                raise serializers.ValidationError({"referral_code": "You cannot use your own referral code"})
        return data

    def create(self, validated_data):
        identifier = validated_data["identifier"]
        username = validated_data["username"]
        referral_code = validated_data.get("referral_code")
        otp = str(random.randint(100000, 999999))

        RegistrationOTP.objects.create(
            identifier=identifier,
            username=username,
            referral_code=referral_code,
            otp=otp,
        )

        if "@" in identifier:
            send_registration_otp_email(identifier, otp)
        else:
            # send_registration_otp_sms(identifier, otp)
            pass

        return {
            "message": "One-time password sent for verification",
            "identifier": identifier,
        }


class ResentOTPSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    username = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    referral_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_identifier(self, value):
        value = value.strip()
        is_email = bool(re.match(r"[^@]+@[^@]+\.[^@]+", value))
        is_phone = bool(value.isdigit() and len(value) >= 7)

        if not (is_email or is_phone):
            raise serializers.ValidationError("Must be a valid email address or phone number")
        return value

    def create(self, validated_data):
        identifier = validated_data["identifier"]
        username = validated_data.get("username")
        referral_code = validated_data.get("referral_code")
        otp = str(random.randint(100000, 999999))

        RegistrationOTP.objects.create(
            identifier=identifier,
            username=username,
            referral_code=referral_code,
            otp=otp,
        )

        if "@" in identifier:
            send_registration_otp_email(identifier, otp)
        else:
            # send_registration_otp_sms(identifier, otp)
            pass

        return {
            "message": "OTP resent successfully",
            "identifier": identifier,
            "otp": otp,
        }


class EmailOTPVerifySerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    otp = serializers.CharField(max_length=6, required=True)
    password = serializers.CharField(write_only=True, required=True)
    referral_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_referral_code(self, value):
        if value:
            value = value.strip()
            if not User.objects.filter(referral_code=value, is_active=True).exists():
                raise serializers.ValidationError("Invalid referral code")
        return value

    def validate(self, data):
        identifier = data.get("identifier", "").strip()
        otp_input = data.get("otp", "").strip()

        otp_instance = RegistrationOTP.objects.filter(identifier=identifier).order_by("-created_at").first()
        if not otp_instance:
            raise serializers.ValidationError({"message": "Invalid OTP or identifier"})

        if otp_instance.otp != otp_input:
            raise serializers.ValidationError({"message": "Invalid OTP"})

        if not otp_instance.is_valid(otp_input):
            raise serializers.ValidationError({"message": "OTP expired or already used"})

        # Resolve referral code
        referral_code = data.get("referral_code") or (otp_instance.referral_code if otp_instance else None)
        referrer = None
        if referral_code:
            referrer = User.objects.filter(referral_code=referral_code, is_active=True).first()
            if not referrer:
                raise serializers.ValidationError({"message": "Invalid referral code"})

            # Prevent self-referral
            if (
                referrer.email == identifier
                or referrer.phone == identifier
                or (otp_instance and otp_instance.username and referrer.username == otp_instance.username)
            ):
                raise serializers.ValidationError({"message": "You cannot use your own referral code"})

        data["otp_instance"] = otp_instance
        data["referrer"] = referrer
        return data

    def create(self, validated_data):
        identifier = validated_data["identifier"].strip()
        password = validated_data["password"]
        otp_instance = validated_data.get("otp_instance")
        referrer = validated_data.get("referrer")

        username = (otp_instance.username if otp_instance and otp_instance.username else None) or identifier
        is_phone = identifier.isdigit()

        # ---------------------------------------
        # CHECK IF USER ALREADY EXISTS
        # ---------------------------------------
        if is_phone:
            user = User.objects.filter(phone=identifier).first()
        else:
            user = User.objects.filter(email__iexact=identifier).first()
        if user:
            user.set_password(password)
            if referrer and not user.referred_by:
                user.referred_by = referrer

            if is_phone:
                user.is_phone_verified = True
            else:
                user.is_email_verified = True

            user.save()

        else:
            # ---------------------------------------
            # CREATE NEW USER
            # ---------------------------------------
            if is_phone:
                user = User.objects.create_user(
                    username=username,
                    phone=identifier,
                    password=password,
                    referred_by=referrer,
                )
                user.is_phone_verified = True
            else:
                user = User.objects.create_user(
                    username=username,
                    email=identifier,
                    password=password,
                    referred_by=referrer,
                )
                user.is_email_verified = True

            user.save()

            # Place in binary referral network tree
            if referrer:
                from Applications.Referrals.referral_utils import place_user_in_referral_tree
                place_user_in_referral_tree(user, referrer)

        # ---------------------------------------
        # CLEANUP OTP
        # ---------------------------------------
        RegistrationOTP.objects.filter(identifier=identifier).delete()

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "unique_id",
            "username",
            "email",
            "phone",
            "fullname",
            "role",
            "department",
            "avatar",
            "is_verified",
            "referral_code",
            "referred_by",
            "is_email_verified",
            "is_phone_verified",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "unique_id",
            "referral_code",
            "referred_by",
            "date_joined",
        ]


class FranchisePartnerSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        from .auth_models import FranchisePartner
        model = FranchisePartner
        fields = '__all__'


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        from .auth_models import AuditLog
        model = AuditLog
        fields = '__all__'


class SecurityGateVerifySerializer(serializers.Serializer):
    pin = serializers.CharField(required=True, write_only=True)

