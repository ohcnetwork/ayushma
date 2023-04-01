from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer


class AuthSerializer(AuthTokenSerializer):
    email = serializers.EmailField(label=_("Username"), write_only=True)
    username = None

    def validate(self, attrs):
        attrs["username"] = attrs.get("email")
        return super().validate(attrs)
