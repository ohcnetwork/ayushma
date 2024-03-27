import openai
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from ayushma.models import APIKey, Chat
from ayushma.models.enums import STTEngine
from ayushma.serializers import ChatDetailSerializer, ConverseSerializer
from ayushma.utils.converse import converse_api
from ayushma.utils.speech_to_text import speech_to_text
from utils.views.base import BaseModelViewSet
from utils.views.mixins import PartialUpdateModelMixin

PREDEFINED_CONFIGS = {
    "ai_form_fill": {
        "model": "gpt-4-turbo-preview",
        "response_format": "json_object",
        "max_tokens": 4096,
        "temperature": 0,
    },
}


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class APIKeyAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.headers.get("X-API-KEY"):
            api_key = request.headers.get("X-API-KEY")
            try:
                APIKey.objects.get(key=api_key)
                return True
            except APIKey.DoesNotExist:
                return False


class OrphanChatViewSet(
    BaseModelViewSet,
    PartialUpdateModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
):
    queryset = Chat.objects.all()
    serializer_class = ChatDetailSerializer
    permission_classes = (APIKeyAuth,)
    lookup_field = "external_id"
    serializer_action_classes = {
        "converse": ConverseSerializer,
    }

    def initialize_request(self, request, *args, **kwargs):
        self.action = self.action_map.get(request.method.lower())
        return super().initialize_request(request, *args, **kwargs)

    def get_parsers(self):
        if self.action == "converse":
            return [MultiPartParser()]
        return super().get_parsers()

    def get_queryset(self):
        api_key = self.request.headers.get("X-API-KEY")
        key = APIKey.objects.get(key=api_key)
        queryset = self.queryset.filter(api_key=key)
        return queryset

    def create(self, request, *args, **kwargs):
        message = self.request.data.pop("message", None)

        do_create = super().create(request, *args, **kwargs)

        if message:
            chat = Chat.objects.get(external_id=do_create.data["external_id"])
            self.request.data.update(message)
            try:
                response = converse_api(
                    request=self.request,
                    chat=chat,
                    is_thread=False,
                )
                return Response(
                    {
                        **do_create.data,
                        "response": response.data,
                    }
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return do_create

    def perform_create(self, serializer):
        api_key = self.request.headers.get("X-API-KEY")
        key = APIKey.objects.get(key=api_key)

        serializer.save(api_key=key)

    @extend_schema(
        tags=("orphan_chats",),
    )
    @action(detail=True, methods=["post"])
    def converse(self, *args, **kwarg):
        chat: Chat = Chat.objects.get(external_id=kwarg["external_id"])
        try:
            response = converse_api(
                request=self.request,
                chat=chat,
                is_thread=False,
            )
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def transcribe(self, request, *args, **kwargs):
        language = request.data.get("language") or "en"
        audio = request.data.get("audio")
        engine = request.data.get("engine")
        if not audio or not engine:
            raise ValidationError("audio and engine are required")
        try:
            engine_id = STTEngine.get_id_from_name(engine)
            transcript = speech_to_text(engine_id, audio, language + "-IN")
            return Response({"transcript": transcript})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def completion(self, request, *args, **kwargs):
        task = request.data.get("task")

        if not task:
            raise ValidationError("task is required")

        config = PREDEFINED_CONFIGS.get(task)

        if not config:
            raise ValidationError("Invalid task")

        model = config.get("model")
        response_format = config.get("response_format")
        max_tokens = config.get("max_tokens")
        temperature = config.get("temperature")

        messages = request.data.get("messages")
        if not messages or len(messages) == 0:
            raise ValidationError("audio and engine are required")
        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            completion = client.chat.completions.create(
                model=model,
                temperature=temperature,
                response_format={"type": response_format},
                messages=messages,
                max_tokens=max_tokens,
            )

            ai_response = completion.choices[0].message.content
            return Response({"response": ai_response})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
