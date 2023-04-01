import requests
from django.db.models import Count, Exists, OuterRef
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.settings.base import CDN_KEY
from utils.views.base import BaseModelViewSet
from ayushma.serializers.users import UserPublicSerializer

from ..models import Follow, UploadType, User
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
