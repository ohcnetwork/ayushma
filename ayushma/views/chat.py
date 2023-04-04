import openai
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import authentication, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..utils.openaiapi import get_embedding

import tiktoken

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


class ChatViewSet(APIView):
    """
    View to convert text to vector embeddings using OpenAI's API
    """

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=("chat",),
        operation_id="text-to-vector",
    )
    def post(self, request):
        
        text = request.data.get("text")
        openai.api_key = settings.OPENAI_API_KEY
        num_tokens = num_tokens_from_string(text, "cl100k_base")
        
        if num_tokens < 8192:
            embedding = get_embedding(text=text)
            return Response({"embedding": embedding})
        else:
            res = []
            parts = split_text(text)
            for part in parts:
                res.append({"embedding": get_embedding(text=part)})
            return Response({"embeddings": res})
