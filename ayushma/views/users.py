from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions
from rest_framework.decorators import action

from utils.views.base import BaseModelViewSet

from ..models import User
from ..permissions import IsSelfOrReadOnly
from ..serializers import UserDetailSerializer, UserSerializer


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
    permission_classes = (IsSelfOrReadOnly,)
    serializer_action_classes = {
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

    def destroy(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    @action(detail=False)
    def me(self, *args, **kwargs):
        """Get current user"""
        return super().retrieve(*args, **kwargs)

    @me.mapping.patch
    def partial_update_me(self, request, *args, **kwargs):
        """Update current user"""
        return super().partial_update(request, *args, **kwargs)
