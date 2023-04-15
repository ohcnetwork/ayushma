from rest_framework import serializers

from ayushma.models import Chat


class ChatSerializer(serializers.ModelSerializer):

    allow_key = serializers.BooleanField(default=False)

    class Meta:
        model = Chat
        fields = ("external_id", "title", "created_at", "modified_at", "namespace", "allow_key")
        read_only_fields = ("external_id", "created_at", "modified_at")
