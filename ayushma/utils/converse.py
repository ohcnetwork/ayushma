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
from ayushma.serializers import (
    ChatDetailSerializer,
    ChatMessageSerializer,
    ChatSerializer,
)
from ayushma.utils.language_helpers import translate_text
from ayushma.utils.openaiapi import converse
from utils.views.base import BaseModelViewSet


def converse_api(
    request,
    chat,
):
    audio = request.data.get("audio")
    text = request.data.get("text")
    language = request.data.get("language") or "en"
    open_ai_key = request.headers.get("OpenAI-Key") or (
        request.user.allow_key and settings.OPENAI_API_KEY
    )
    top_k = request.data.get("top_k") or 100
    temperature = request.data.get("temperature") or 0.1
    stream = request.data.get("stream")
    generate_audio = request.data.get("generate_audio")

    converse_type = "audio" if audio else "text"

    # convert stream to boolean
    if type(stream) != bool:
        if stream == "false":
            stream = False
        else:
            stream = True

    if type(generate_audio) != bool:
        if generate_audio == "false":
            generate_audio = False
        else:
            generate_audio = True

    if not open_ai_key:
        return Response(
            {"error": "OpenAI-Key header is required to create a chat"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    stats = dict()

    # logging request

    print(
        f"""
    Request:
    type: {converse_type}
    chat: {chat}
    audio: {audio}
    text: {text}
    language: {language}
    open_ai_key: {open_ai_key}
    top_k: {top_k}
    temperature: {temperature}
    stream: {stream}
    generate_audio: {generate_audio}
    """
    )

    # store time to complete request
    stats["start_time"] = time.time()
    if converse_type == "audio" and not audio:
        return Exception("Please provide audio to generate transcript")
    if converse_type == "text" and not text:
        return Exception("Please provide text to generate transcript")

    if converse_type == "audio":
        stats["transcript_start_time"] = time.time()
        transcript = openai.Audio.translate(
            "whisper-1", file=audio, api_key=open_ai_key
        )
        stats["transcript_end_time"] = time.time()

        english_text = transcript.text

    elif converse_type == "text":
        english_text = text
        if language != "en":
            stats["request_translation_start_time"] = time.time()
            english_text = translate_text("en-IN", text)
            stats["request_translation_end_time"] = time.time()

    translated_text = english_text
    if language != "en":
        stats["request_translation_start_time"] = time.time()
        translated_text = translate_text(language + "-IN", english_text)
        stats["request_translation_end_time"] = time.time()

    if not ChatMessage.objects.filter(chat=chat).exists():
        chat.title = translated_text[0:50]
        chat.save()

    if stream == True:
        response = StreamingHttpResponse(content_type="text/event-stream")
        response.streaming_content = converse(
            english_text=english_text,
            local_translated_text=translated_text,
            openai_key=open_ai_key,
            chat=chat,
            match_number=top_k,
            stats=stats,
            temperature=temperature,
            user_language=language + "-IN",
            generate_audio=generate_audio,
        )
    else:
        response_message = converse(
            english_text=english_text,
            local_translated_text=translated_text,
            openai_key=open_ai_key,
            chat=chat,
            match_number=top_k,
            stats=stats,
            temperature=temperature,
            user_language=language + "-IN",
            stream=False,
            generate_audio=generate_audio,
        )

        # convert yielded response to list

        response_message = list(response_message)[0]

        return Response(
            ChatMessageSerializer(response_message).data, status=status.HTTP_200_OK
        )

    return response
