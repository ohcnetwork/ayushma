from rest_framework import serializers

from ayushma.models import Chat, ChatMessage
from ayushma.serializers.project import ProjectSerializer


class ChatSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = ("external_id", "title", "created_at", "modified_at", "project")
        read_only_fields = ("external_id", "created_at", "modified_at", "project")


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
    chats = ChatMessageSerializer(many=True, read_only=True, source="chatmessage_set")

    class Meta:
        model = Chat
        fields = ("external_id", "title", "created_at", "modified_at", "chats")
        read_only_fields = ("external_id", "created_at", "modified_at")
