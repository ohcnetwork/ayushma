from rest_framework import serializers

from ayushma.models import Chat, ChatMessage
from ayushma.serializers.project import ProjectSerializer


class ChatSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = (
            "external_id",
            "title",
            "created_at",
            "modified_at",
            "project",
            "language",
        )
        read_only_fields = (
            "external_id",
            "created_at",
            "modified_at",
            "project",
        )


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
    chats = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ("external_id", "title", "created_at", "modified_at", "chats")
        read_only_fields = ("external_id", "created_at", "modified_at")

    def get_chats(self, obj):
        chatmessages = ChatMessage.objects.filter(chat=obj).order_by("created_at")
        return ChatMessageSerializer(chatmessages, many=True).data
