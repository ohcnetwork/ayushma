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

def n_equal_strings(str):
    """Returns one string split into n equal length strings"""
    n = len(str)
    number_of_strings = int(n / 8192) 
    number_of_chars = int(n / number_of_strings)
    equalStr = []

    for i in range(0, n, number_of_chars):
        try:
            part = str[i : i + number_of_chars]
            equalStr.append(part)
        except:
            part = str[i : ]
            equalStr.append(part)
    
    return equalStr


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
            equalStrs = n_equal_strings(text)
            for str in equalStrs:
                res.append({"embedding": get_embedding(text=str)})
            return Response({"embeddings": res})
