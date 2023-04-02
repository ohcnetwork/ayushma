import openai
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import authentication, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from ..utils.openaiapi import get_embedding


class TextToVector(APIView):
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
        embedding = get_embedding(text=text)
        return Response({"embedding": embedding})
