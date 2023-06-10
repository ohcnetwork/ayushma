from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.decorators import action

from ayushma.models import User
from ayushma.serializers.users import (
    UserCreateSerializer,
    UserDetailSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from utils.views.base import BaseModelViewSet


class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = (permissions.IsAdminUser,)
    serializer_action_classes = {
        "register": UserCreateSerializer,
        "list": UserSerializer,
        "update": UserUpdateSerializer,
        "partial_update": UserUpdateSerializer,
    }
    permission_action_classes = {
        "me": (permissions.IsAuthenticated(),),
        "partial_update_me": (permissions.IsAuthenticated(),),
    }
    lookup_field = "username"

    def get_object(self):
        return (
            super().get_object()
            if self.kwargs.get(self.lookup_field)
            else self.get_queryset().get(pk=self.request.user.id)
        )

    @extend_schema(tags=["users"])
    @action(detail=False)
    def me(self, *args, **kwargs):
        """Get current user"""
        return super().retrieve(*args, **kwargs)

    @extend_schema(tags=["users"])
    @me.mapping.patch
    def partial_update_me(self, request, *args, **kwargs):
        """Update current user"""
        return super().partial_update(request, *args, **kwargs)
