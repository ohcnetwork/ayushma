from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from ayushma.models import APIKey, Chat
from ayushma.serializers import ChatDetailSerializer, ConverseSerializer
from ayushma.utils.converse import converse_api
from utils.views.base import BaseModelViewSet


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class APIKeyAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.headers.get("X-API-KEY"):
            api_key = request.headers.get("X-API-KEY")
            try:
                APIKey.objects.filter(key=api_key).exists()
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
            )
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
