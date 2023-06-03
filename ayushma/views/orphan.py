import time

import openai
from django.conf import settings
from django.http import StreamingHttpResponse
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.serializers import CharField, IntegerField

from ayushma.models import APIKey, Chat, ChatMessage, Project
from ayushma.serializers import ChatDetailSerializer, ConverseSerializer
from ayushma.utils.converse import converse_api
from ayushma.utils.language_helpers import translate_text
from ayushma.utils.openaiapi import converse
from utils.views.base import BaseModelViewSet

from .chat import ChatViewSet


class APIKeyAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.headers.get("X-API-KEY"):
            api_key = request.headers.get("X-API-KEY")
            try:
                key = APIKey.objects.get(key=api_key)
                return True
            except APIKey.DoesNotExist:
                return False


@extend_schema_view(
    tags=("orphan_chats",),
    destroy=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=False),
    create=extend_schema(exclude=False),
    retrieve=extend_schema(
        description="Advanced Chats",
    ),
)
class OrphanChatViewSet(BaseModelViewSet):
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

    def perform_create(self, serializer):
        if (
            not self.request.headers.get("OpenAI-Key")
            and not self.request.user.allow_key
        ):
            raise ValidationError(
                {"error": "OpenAI-Key header is required to create a chat"}
            )

        api_key = self.request.headers.get("X-API-KEY")
        key = APIKey.objects.get(key=api_key)

        serializer.save(api_key=key)
        super().perform_create(serializer)

    @extend_schema(
        tags=("orphan_chats",),
    )
    @action(detail=True, methods=["post"])
    def converse(self, *args, **kwarg):
        chat: Chat = Chat.objects.get(external_id=kwarg["external_id"])
        # try:
        response = converse_api(
            request=self.request,
            chat=chat,
        )
        return response
        # except Exception as e:
        #    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
