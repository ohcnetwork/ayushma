from rest_framework import serializers

from ayushma.models import Chat, ChatMessage


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ("external_id", "title", "created_at", "modified_at", "namespace")
        read_only_fields = ("external_id", "created_at", "modified_at")


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = (
            "external_id",
            "chat",
            "messageType",
            "message",
            "created_at",
            "modified_at",
        )
        read_only_fields = ("external_id", "created_at", "modified_at")


class ChatDetailSerializer(serializers.ModelSerializer):
    chats = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ("external_id", "title", "created_at", "modified_at", "chats")
        read_only_fields = ("external_id", "created_at", "modified_at", "chats")
