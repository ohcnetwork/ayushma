from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from ayushma.models import User
from utils.helpers import validatecaptcha


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "external_id",
            "username",
            "full_name",
            "email",
            "allow_key",
            "is_staff",
            "is_reviewer",
            "date_joined",
        )


class UserCreateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    recaptcha = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("username", "full_name", "password", "email", "recaptcha")

    def validate_recaptcha(self, value):
        if not validatecaptcha(value):
            raise serializers.ValidationError("Invalid captcha")
        return value

    def validate(self, validated_data):
        validated_data.pop("recaptcha", None)
        return validated_data

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)


class UserDetailSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "external_id",
            "username",
            "full_name",
            "email",
            "allow_key",
            "is_staff",
            "is_reviewer",
            "password",
            "date_joined",
        )
        read_only_fields = (
            "external_id",
            "email",
            "username",
            "allow_key",
            "is_staff",
            "is_reviewer",
            "date_joined",
        )

    def update(self, instance, validated_data):
        if password := validated_data.pop("password", None):
            instance.set_password(password)
        return super().update(instance, validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "full_name", "allow_key", "is_staff", "is_reviewer")
