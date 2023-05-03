from datetime import timedelta

from django.conf import settings
from django.contrib.auth.password_validation import (
    get_password_validators,
    validate_password,
)
from django.core.exceptions import ValidationError
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ayushma.models.token import ResetPasswordToken
from ayushma.models.users import User
from ayushma.serializers.token import (
    PasswordTokenSerializer,
    ResetPasswordUserSerializer,
    ResetTokenSerializer,
)
from ayushma.signals.token import reset_password_token_created

HTTP_USER_AGENT_HEADER = getattr(
    settings,
    "DJANGO_REST_PASSWORDRESET_HTTP_USER_AGENT_HEADER",
    "HTTP_USER_AGENT",
)
HTTP_IP_ADDRESS_HEADER = getattr(
    settings, "DJANGO_REST_PASSWORDRESET_IP_ADDRESS_HEADER", "REMOTE_ADDR"
)


class ResetPasswordViewset(GenericViewSet):
    permission_classes = (AllowAny,)
    serializer_class = PasswordTokenSerializer

    def get_serializer_class(self):
        if self.action == "forgot":
            return ResetPasswordUserSerializer
        elif self.action == "verify":
            return ResetTokenSerializer
        return super().get_serializer_class()

    @extend_schema(tags=["auth"])
    @action(detail=False, methods=["POST"], url_name="forgot-password")
    def forgot(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")

        # deleting all the previous expiry tokens
        password_reset_token_validation_time = (
            settings.DJANGO_REST_RESET_TOKEN_EXPIRY_TIME
        )
        expiry_time = timezone.now() - timedelta(
            minutes=password_reset_token_validation_time
        )

        ResetPasswordToken.objects.filter(created_at__lte=expiry_time).delete()

        print("email", email)
        # checking if the user is active or not
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            print("user does not exist")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        print("user", user)
        # creating a new token
        token = None
        if user.password_reset_tokens.all().count() > 0:
            token = user.password_reset_tokens.all()[0]
        else:
            token = ResetPasswordToken.objects.create(
                user=user,
                user_agent=request.META.get(HTTP_USER_AGENT_HEADER, ""),
                ip_address=request.META.get(HTTP_IP_ADDRESS_HEADER, ""),
            )

        reset_password_token_created.send(
            sender=self.__class__,
            reset_password_token=token,
        )

        return Response(status=status.HTTP_200_OK)

    @extend_schema(tags=["auth"])
    @action(methods=["POST"], detail=False)
    def verify(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data.get("token")
        email = serializer.validated_data.get("email")

        if not ResetPasswordToken.objects.filter(key=token, user__email=email).exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"token": "Invalid token"},
            )

        user = User.objects.get(email=email)
        return Response(
            status=status.HTTP_202_ACCEPTED,
            data={
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
            },
        )

    @extend_schema(tags=["auth"])
    @action(methods=["POST"], detail=False)
    def reset(self, request, *args, **kwargs):
        def validation(password):
            try:
                validate_password(
                    password,
                    user=request.user,
                    password_validators=get_password_validators(
                        settings.AUTH_PASSWORD_VALIDATORS
                    ),
                )
            except ValidationError as e:
                raise serializers.ValidationError({"password": e.messages})

        if request.user.is_authenticated:
            print("user is authenticated")
            password = request.data.get("password")
            validation(password)
            request.user.set_password(password)
            request.user.save()
            return Response(status=status.HTTP_202_ACCEPTED)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data.get("password")
        token = serializer.validated_data.get("token")
        email = serializer.validated_data.get("email")

        # find the token
        try:
            reset_password_token = ResetPasswordToken.objects.get(key=token)
        except ResetPasswordToken.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(email=email)
        if not user.is_active:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # set the new password
        validation(password)
        user.set_password(password)
        user.save()

        # Delete all password reset tokens for this user
        ResetPasswordToken.objects.filter(user=user).delete()

        return Response(status=status.HTTP_202_ACCEPTED)
