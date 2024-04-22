from rest_framework import permissions
from rest_framework.mixins import CreateModelMixin

from ayushma.models import APIKey
from ayushma.serializers.services import TempTokenSerializer
from utils.views.base import BaseModelViewSet


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class APIKeyAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.headers.get("X-API-KEY"):
            api_key = request.headers.get("X-API-KEY")
            return APIKey.objects.filter(key=api_key).exists()


class TempTokenViewSet(BaseModelViewSet, CreateModelMixin):
    serializer_class = TempTokenSerializer
    permission_classes = (APIKeyAuth,)
    lookup_field = "external_id"

    def perform_create(self, serializer):
        api_key = self.request.headers.get("X-API-KEY")
        key = APIKey.objects.get(key=api_key)

        serializer.save(api_key=key)
