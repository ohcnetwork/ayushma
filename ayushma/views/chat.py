from typing import List

import openai
import tiktoken
from django.conf import settings
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from langchain.schema import AIMessage, HumanMessage
from pinecone import QueryResponse
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.serializers import CharField, IntegerField

from ayushma.models import Chat, ChatMessage, Project
from ayushma.serializers import ChatDetailSerializer, ChatSerializer
from ayushma.utils.langchain import LangChainHelper
from ayushma.utils.openaiapi import get_embedding, get_sanitized_reference
from utils.views.base import BaseModelViewSet


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def split_text(text):
    """Returns one string split into n equal length strings"""
    n = len(str)
    number_of_chars = 8192
    parts = []

    for i in range(0, n, number_of_chars):
        part = text[i : i + number_of_chars]
        parts.append(part)

    return parts


@extend_schema_view(
    destroy=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=False),
    create=extend_schema(exclude=False),
    retrieve=extend_schema(
        description="Get Chats",
    ),
)
class ChatViewSet(BaseModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    serializer_action_classes = {
        "retrieve": ChatDetailSerializer,
    }
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "external_id"

    def get_queryset(self):
        project_id = self.kwargs["project_external_id"]
        queryset = self.queryset.filter(
            user=self.request.user, project__external_id=project_id
        )
        return queryset

    def perform_create(self, serializer):
        if (
            not self.request.headers.get("OpenAI-Key")
            and not self.request.user.allow_key
        ):
            raise ValidationError(
                {"error": "OpenAI-Key header is required to create a chat"}
            )

        project_id = self.kwargs["project_external_id"]
        project = Project.objects.get(external_id=project_id)

        serializer.save(user=self.request.user, project=project)
        super().perform_create(serializer)

    @extend_schema(
        tags=("chats",),
        request=inline_serializer(
            name="ConverseRequest",
            fields={
                "text": CharField(),
                "match_number": IntegerField(default=10),
            },
        ),
        responses={status.HTTP_200_OK: None},
    )
    @action(detail=True, methods=["post"])
    def converse(self, *args, **kwarg):
        if not self.request.data.get("text"):
            return Response(
                {"error": "Please provide text to generate embedding"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        text = self.request.data.get("text")

        chat = Chat.objects.get(external_id=kwarg["external_id"])

        openai_key = self.request.headers.get("OpenAI-Key") or (
            self.request.user.allow_key and settings.OPENAI_API_KEY
        )
        if not openai_key:
            raise ValidationError(
                {"error": "OpenAI-Key header is required to create a chat or converse"}
            )
        openai.api_key = openai_key

        text = text.replace("\n", " ")

        nurse_query = ChatMessage.objects.create(message=text, chat=chat, messageType=1)

        num_tokens = num_tokens_from_string(text, "cl100k_base")

        embeddings: List[List[List[float]]] = []

        if num_tokens < 8192:
            try:
                embeddings.append(get_embedding(text=[text], openai_api_key=openai_key))
            except Exception as e:
                return Response(
                    {"error": e.__str__()},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            parts = split_text(text)
            for part in parts:
                try:
                    embeddings.append(
                        get_embedding(text=[part], openai_api_key=openai_key)
                    )
                except Exception as e:
                    return Response(
                        {"error": e.__str__()},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        # find similar embeddings from pinecone index for each embedding
        pinecone_references: List[QueryResponse] = []
        top_k = self.request.data.get("match_number") or 100
        for embedding in embeddings:
            try:
                similar: QueryResponse = settings.PINECONE_INDEX_INSTANCE.query(
                    vector=embedding,
                    top_k=top_k,
                    namespace=str(chat.project.external_id),
                    include_metadata=True,
                )

                pinecone_references.append(similar)
            except Exception as e:
                return Response(
                    {"error": e.__str__()},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        reference = get_sanitized_reference(pinecone_references=pinecone_references)

        lang_chain_helper = LangChainHelper(
            openai_api_key=openai_key, prompt_template=chat.project.prompt
        )

        # excluding the latest query since it is not a history
        previous_messages = (
            ChatMessage.objects.filter(chat=chat)
            .exclude(id=nurse_query.id)
            .order_by("created_at")
        )

        chat_history = []
        for message in previous_messages:
            if message.messageType == 1:  # type=USER
                chat_history.append(HumanMessage(content=f"Nurse: {message.message}"))
            elif message.messageType == 3:  # type=AYUSHMA
                chat_history.append(AIMessage(content=f"Ayushma: {message.message}"))

        response = lang_chain_helper.get_response(
            user_msg=text, reference=reference, chat_history=chat_history
        )

        response = response.replace("Ayushma: ", "")

        ChatMessage.objects.create(message=response, chat=chat, messageType=3)

        return Response({"answer": response})
