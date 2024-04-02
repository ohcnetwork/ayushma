from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ayushma.serializers.auth import AuthSerializer
from ayushma.serializers.users import UserCreateSerializer


class AuthViewSet(GenericViewSet):
    serializer_class = AuthSerializer
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == "register":
            return UserCreateSerializer
        return super().get_serializer_class()

    @extend_schema(
        request=UserCreateSerializer,
        responses={
            201: OpenApiResponse(
                description="User created",
            )
        },
        tags=["auth"],
    )
    @action(detail=False, methods=["POST"])
    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(tags=["auth"])
    @action(detail=False, methods=["POST"])
    def login(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})

    @extend_schema(tags=["auth"])
    @action(detail=False, methods=["DELETE"])
    def logout(self, request, *args, **kwargs):
        if auth_token := request.auth:
            Token.objects.filter(key=auth_token).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise ParseError("No auth token provided")
