import time

from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from ayushma.models import APIKey, ChatMessage
from ayushma.serializers import ChatMessageSerializer
from ayushma.utils.language_helpers import translate_text
from ayushma.utils.openaiapi import converse
from ayushma.utils.speech_to_text import speech_to_text


def converse_api(
    request,
    chat,
):
    if request.headers.get("X-API-KEY"):
        api_key = request.headers.get("X-API-KEY")
        key: APIKey = APIKey.objects.get(key=api_key)
        user = key.creator
    else:
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        user = request.user

    audio = request.data.get("audio")
    text = request.data.get("text")
    language = request.data.get("language") or "en"
    open_ai_key = request.headers.get("OpenAI-Key") or (
        user.allow_key and settings.OPENAI_API_KEY
    )
    noonce = request.data.get("noonce")

    if noonce:
        try:
            ChatMessage.objects.get(noonce=noonce)
            return Response(
                {"error": "This noonce has already been used"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ChatMessage.DoesNotExist:
            pass

    if not open_ai_key:
        raise ValidationError(
            {"error": "OpenAI-Key header is required to create a chat"}
        )

    project = chat.project
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
        transcript = speech_to_text(project.stt_engine, audio, language + "-IN")
        stats["transcript_end_time"] = time.time()
        translated_text = transcript

    elif converse_type == "text":
        translated_text = text

    if language != "en":
        stats["request_translation_start_time"] = time.time()
        english_text = translate_text("en-IN", translated_text)
        stats["request_translation_end_time"] = time.time()
    else:
        english_text = translated_text

    if not ChatMessage.objects.filter(chat=chat).exists():
        chat.title = translated_text[0:50]
        chat.save()

    if stream:
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
