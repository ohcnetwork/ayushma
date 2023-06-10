from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from ayushma.models.token import ResetPasswordToken
from ayushma.models.users import User


class PasswordValidateMixin:
    def validate(self, data):
        token = data.get("token")
        email = data.get("email")

        password_reset_token_validation_time = (
            settings.DJANGO_REST_RESET_TOKEN_EXPIRY_TIME
        )

        try:
            reset_password_token = ResetPasswordToken.objects.get(key=token)
        except (
            ValueError,
            ValidationError,
            ResetPasswordToken.DoesNotExist,
        ):
            raise ValidationError(
                {
                    "token": _(
                        "The OTP password entered is not valid. Please check and try again.",
                    )
                },
            )

        expiry_date = reset_password_token.created_at + timedelta(
            minutes=password_reset_token_validation_time
        )

        if timezone.now() > expiry_date:
            reset_password_token.delete()
            raise ValidationError(
                {
                    "token": _(
                        "The OTP password has expired. Please try again.",
                    )
                },
            )

        user = User.objects.get(email=email)
        if reset_password_token.user != user:
            raise ValidationError(
                {
                    "token": _(
                        "The OTP password entered is not valid. Please check and try again.",
                    )
                },
            )
        if not user.is_active:
            raise ValidationError(
                {
                    "detail": _(
                        "This account is inactive. Please contact admin.",
                    )
                },
            )
        return data


class PasswordTokenSerializer(PasswordValidateMixin, serializers.Serializer):
    password = serializers.CharField()
    token = serializers.CharField()
    email = serializers.EmailField()


class ResetTokenSerializer(PasswordValidateMixin, serializers.Serializer):
    token = serializers.CharField()
    email = serializers.EmailField()


class ResetPasswordUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
