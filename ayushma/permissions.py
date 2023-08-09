from ipaddress import ip_address

from django.utils import timezone
from rest_framework import permissions

from ayushma.models.services import TempToken
from utils.helpers import get_client_ip


class IsSelfOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


class IsUserOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsTempTokenOrAuthenticated(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        auth_token: str = request.headers.get("Authorization")
        auth_token = auth_token.split(" ")[1]
        if auth_token.startswith("tt"):
            temptoken: TempToken = TempToken.objects.get(token=auth_token)
            ip_address = get_client_ip(request)
            if ip_address == temptoken.ip and temptoken.expires_at > timezone.now():
                request.user = temptoken.api_key.service.owner
                request.is_authenticated = True
                request.service = temptoken.api_key.service
                return True
        return bool(request.user and request.user.is_authenticated)
