from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from ..models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "username",
            "full_name",
        )


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "external_id",
            "username",
            "full_name",
            "email",
        )
        read_only_fields = (
            "external_id",
            "email",
            "username",
        )

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        if password := validated_data.pop("password", None):
            instance.set_password(password)
        return super().update(instance, validated_data)