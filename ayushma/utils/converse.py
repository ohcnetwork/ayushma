import time

from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework import status
from rest_framework.response import Response

from ayushma.models import APIKey, ChatMessage
from ayushma.models.services import Service
from ayushma.serializers import ChatMessageSerializer
from ayushma.utils.language_helpers import translate_text
from ayushma.utils.openaiapi import converse, converse_thread
from ayushma.utils.speech_to_text import speech_to_text


def converse_api(
    request,
    chat,
    is_thread,
):
    if request.headers.get("X-API-KEY"):
        api_key = request.headers.get("X-API-KEY")
        key: APIKey = APIKey.objects.get(key=api_key)
        user = key.creator
    else:
        if not is_thread and not request.user.is_authenticated:
            return Response(
                {"error": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        user = request.user

    audio = request.data.get("audio")
    text = request.data.get("text")
    language = request.data.get("language") or "en"

    try:
        service: Service = request.service
    except AttributeError:
        service = None

    open_ai_key = None
    if (service and service.allow_key) or is_thread:
        open_ai_key = settings.OPENAI_API_KEY

    if not is_thread:
        if not open_ai_key:
            open_ai_key = (
                request.headers.get("OpenAI-Key")
                or (chat.project and chat.project.openai_key)
                or (user.allow_key and settings.OPENAI_API_KEY)
            )
        noonce = request.data.get("noonce")

        if noonce and ChatMessage.objects.filter(noonce=noonce).exists():
            return Response(
                {"error": "This noonce has already been used"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not open_ai_key:
            return Response(
                {"error": "OpenAI-Key header is required to create a chat"},
                status=status.HTTP_400_BAD_REQUEST,
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

    if is_thread:
        stream = False  # Threads do not support streaming

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
    is_thread: {is_thread}
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
        if request.data.get("transcript_start_time") and request.data.get(
            "transcript_end_time"
        ):
            stats["transcript_start_time"] = request.data["transcript_start_time"]
            stats["transcript_end_time"] = request.data["transcript_end_time"]
        translated_text = text

    if language != "en":
        stats["request_translation_start_time"] = time.time()
        english_text = translate_text("en-IN", translated_text)
        stats["request_translation_end_time"] = time.time()
    else:
        english_text = translated_text

    if not is_thread:
        if not ChatMessage.objects.filter(chat=chat).exists():
            chat.title = translated_text[0:50]
            chat.save()
    else:
        response_message = converse_thread(
            thread=chat,
            english_text=english_text,
            openai_key=open_ai_key,
        )

        return Response(
            {
                "message": response_message,
            },
            status=status.HTTP_200_OK,
        )

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
            noonce=noonce,
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
            noonce=noonce,
        )

        # convert yielded response to list

        response_message = list(response_message)[0]

        return Response(
            ChatMessageSerializer(response_message).data, status=status.HTTP_200_OK
        )

    return response
