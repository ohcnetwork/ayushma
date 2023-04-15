from typing import List

import openai
import tiktoken
from django.conf import settings
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from pinecone import QueryResponse
from rest_framework import authentication, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import CharField, IntegerField

from utils.views.base import BaseModelViewSet

from ..models import Chat
from ..serializers import ChatSerializer
from ..utils.langchain import LangChainHelper
from ..utils.openaiapi import get_embedding, get_sanitized_reference


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
    serializer_action_classes = {
        "list": ChatSerializer,
        "retrieve": ChatSerializer,
        "create": ChatSerializer,
        "update": ChatSerializer,
    }
    permission_classe = (permissions.IsAuthenticated(),)
    lookup_field = "external_id"

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            Response(
                {"error": "Please login to create a chat"},
                status=status.HTTP_400_BAD_REQUEST,
            )
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

        text = text.replace("\n", " ")
        openai.api_key = settings.OPENAI_API_KEY
        num_tokens = num_tokens_from_string(text, "cl100k_base")

        embeddings: List[List[List[float]]] = []

        if num_tokens < 8192:
            embeddings.append(get_embedding(text=[text]))

        else:
            parts = split_text(text)
            for part in parts:
                embeddings.append(get_embedding(text=[part]))

        # find similar embeddings from pinecone index for each embedding
        pinecone_references: List[QueryResponse] = []
        top_k = self.request.data.get("match_number") or 10
        for embedding in embeddings:
            similar: QueryResponse = settings.PINECONE_INDEX_INSTANCE.query(
                vector=embedding,
                top_k=top_k,
                namespace=chat.namespace,
                include_metadata=True,
            )

            pinecone_references.append(similar)

        reference = get_sanitized_reference(pinecone_references=pinecone_references)

        lang_chain_helper = LangChainHelper()

        return Response(
            {
                "answer": lang_chain_helper.get_response(
                    user_msg=text, reference=reference
                )
            }
        )
