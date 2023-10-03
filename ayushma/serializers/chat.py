from rest_framework import serializers

from ayushma.models import Chat, ChatFeedback, ChatMessage
from ayushma.serializers.document import DocumentSerializer
from ayushma.serializers.project import ProjectSerializer


class ChatSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Chat
        fields = (
            "external_id",
            "title",
            "created_at",
            "modified_at",
            "username",
            "project",
        )
        read_only_fields = (
            "external_id",
            "created_at",
            "modified_at",
            "username",
            "project",
        )


class ChatMessageSerializer(serializers.ModelSerializer):
    reference_documents = DocumentSerializer(many=True, read_only=True)
    feedback = serializers.SerializerMethodField()
    chat = serializers.CharField(source="chat.external_id")

    class Meta:
        model = ChatMessage
        fields = (
            "external_id",
            "chat",
            "messageType",
            "message",
            "reference_documents",
            "audio",
            "original_message",
            "language",
            "created_at",
            "modified_at",
            "meta",
            "temperature",
            "top_k",
            "feedback",
        )
        read_only_fields = (
            "external_id",
            "created_at",
            "modified_at",
            "reference_documents",
            "meta",
            "audio",
            "original_message",
        )

    def get_feedback(self, obj):
        feedback = ChatFeedback.objects.filter(chat_message=obj).first()
        return ChatFeedbackSerializer(feedback).data if feedback else None


class ChatFeedbackSerializer(serializers.ModelSerializer):
    chat_message = serializers.CharField(source="chat_message.external_id")

    class Meta:
        model = ChatFeedback
        fields = (
            "external_id",
            "chat_message",
            "liked",
            "message",
            "created_at",
            "modified_at",
        )
        read_only_fields = (
            "external_id",
            "created_at",
            "modified_at",
        )

    def create(self, validated_data):
        chat_message_external_id = validated_data.pop("chat_message")["external_id"]
        if not chat_message_external_id:
            raise serializers.ValidationError(
                {"chat_message": "Chat message external id is required"}
            )
        chat_message = ChatMessage.objects.get(external_id=chat_message_external_id)
        feedback = ChatFeedback.objects.create(
            chat_message=chat_message, **validated_data
        )
        return feedback


class ConverseSerializer(serializers.Serializer):
    text = serializers.CharField(required=False)
    audio = serializers.FileField(required=False)
    language = serializers.CharField(default="en")
    top_k = serializers.IntegerField(default=100)
    temperature = serializers.FloatField(default=0.1)
    stream = serializers.BooleanField(default=True)
    generate_audio = serializers.BooleanField(default=True)
    noonce = serializers.CharField(required=False)


class ChatDetailSerializer(serializers.ModelSerializer):
    chats = serializers.SerializerMethodField()
    message = ConverseSerializer(required=False)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Chat
        fields = (
            "external_id",
            "title",
            "username",
            "created_at",
            "modified_at",
            "chats",
            "prompt",
            "message",
            "model",
        )
        read_only_fields = ("external_id", "created_at", "modified_at", "chats", "username")

    def get_chats(self, obj):
        chatmessages = ChatMessage.objects.filter(chat=obj).order_by("created_at")
        context = {"request": self.context.get("request")}
        return ChatMessageSerializer(chatmessages, many=True, context=context).data
