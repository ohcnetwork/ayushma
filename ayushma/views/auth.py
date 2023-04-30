from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ParseError
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from ayushma.serializers import AuthSerializer


class APILoginView(CreateAPIView):
    serializer_class = AuthSerializer
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    @extend_schema(
        tags=("auth",),
        operation_id="api-login",
    )
    def post(self, request: Request):
        """Get auth token"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


class APILogoutView(DestroyAPIView):
    @extend_schema(tags=("auth",), operation_id="api-logout", responses=None)
    def delete(self, request: Request):
        """Destroy auth token"""
        if auth_token := request.auth:
            Token.objects.filter(key=auth_token).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise ParseError("No auth token provided")
