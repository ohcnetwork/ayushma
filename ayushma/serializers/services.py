from rest_framework import serializers

from ayushma.models import TempToken


class TempTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempToken
        fields = ("ip", "token")
        read_only_fields = ("token",)
