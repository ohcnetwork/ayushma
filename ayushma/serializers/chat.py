from rest_framework import serializers

from ayushma.models import Chat, ChatMessage
from ayushma.serializers.document import DocumentSerializer
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
        )
        read_only_fields = (
            "external_id",
            "created_at",
            "modified_at",
            "project",
        )


class ChatMessageSerializer(serializers.ModelSerializer):
    reference_documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = ChatMessage
        fields = (
            "external_id",
            "chat",
            "messageType",
            "message",
            "reference_documents",
            "ayushma_audio_url",
            "original_message",
            "language",
            "created_at",
            "modified_at",
            "meta",
            "temperature",
            "top_k",
        )
        read_only_fields = (
            "external_id",
            "created_at",
            "modified_at",
            "reference_documents",
            "meta",
            "ayushma_audio_url",
            "original_message",
        )


class ChatDetailSerializer(serializers.ModelSerializer):
    chats = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = (
            "external_id",
            "title",
            "created_at",
            "modified_at",
            "chats",
            "prompt",
        )
        read_only_fields = ("external_id", "created_at", "modified_at", "chats")

    def get_chats(self, obj):
        chatmessages = ChatMessage.objects.filter(chat=obj).order_by("created_at")
        return ChatMessageSerializer(chatmessages, many=True).data


class ConverseSerializer(serializers.Serializer):
    text = serializers.CharField(required=False)
    audio = serializers.FileField(required=False)
    language = serializers.CharField(default="en")
    top_k = serializers.IntegerField(default=100)
    temperature = serializers.FloatField(default=0.1)
    stream = serializers.BooleanField(default=True)
    generate_audio = serializers.BooleanField(default=True)
