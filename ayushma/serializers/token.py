from datetime import timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework import status
from django.conf import settings

from ayushma.models.token import ResetPasswordToken


class PasswordValidateMixin:
    def validate(self, data):
        token = data.get("token")

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
                code=status.HTTP_404_NOT_FOUND,
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
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data


class PasswordTokenSerializer(PasswordValidateMixin, serializers.Serializer):
    password = serializers.CharField()
    token = serializers.CharField()


class ResetTokenSerializer(PasswordValidateMixin, serializers.Serializer):
    token = serializers.CharField()
    username = serializers.CharField()


class ResetPasswordUserSerializer(serializers.Serializer):
    username = serializers.CharField()
