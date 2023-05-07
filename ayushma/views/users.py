from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from rest_framework import permissions
from rest_framework.decorators import action

from utils.views.base import BaseModelViewSet
from ayushma.models import User
from ayushma.permissions import IsSelfOrReadOnly
from ayushma.serializers.users import (
    UserCreateSerializer,
    UserDetailSerializer,
    UserSerializer,
)

@extend_schema_view(
    destroy=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
    create=extend_schema(exclude=True),
    retrieve=extend_schema(
        description="Get User",
    ),
)
class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = (IsSelfOrReadOnly, permissions.IsAdminUser)
    serializer_action_classes = {
        "register": UserCreateSerializer,
        "list": UserSerializer,
    }
    permission_action_classes = {
        "me": (permissions.IsAuthenticated(),),
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
