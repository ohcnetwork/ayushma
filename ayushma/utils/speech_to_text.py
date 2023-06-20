import os

import openai
from google.cloud import speech


class WhisperEngine:
    def __init__(self, api_key, language_code):
        self.api_key = api_key
        self.language_code = language_code

    def recognize(self, audio):
        # workaround for setting api version ( https://github.com/openai/openai-python/pull/491 )
        current_api_version = openai.api_version
        openai.api_version = "2020-11-07"
        transcription = openai.Audio.transcribe(
            "whisper-1",
            file=audio,
            language=self.language_code.replace("-IN", ""),
            api_key=self.api_key,
            api_base="https://api.openai.com/v1",
            api_type="open_ai",
            api_version="2020-11-07",  # Bug in openai package, this parameter is ignored
        )
        openai.api_version = current_api_version
        return transcription.text


class GoogleEngine:
    def __init__(self, api_key, language_code):
        self.api_key = api_key
        self.language_code = language_code

    def recognize(self, audio):
        client = speech.SpeechClient()
        audio_content = audio.file.read()
        audio_data = speech.RecognitionAudio(content=audio_content)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
            sample_rate_hertz=48000,
            language_code=self.language_code,
        )

        response = client.recognize(config=config, audio=audio_data)
        if not response.results:
            return ""
        return response.results[0].alternatives[0].transcript


engines = {
    "whisper": WhisperEngine,
    "google": GoogleEngine,
    # Add new engines here
}


def speech_to_text(engine_name, audio, language_code):
    api_key = os.environ.get("STT_API_KEY", "")

    engine_class = engines.get(engine_name)
    if not engine_class:
        raise ValueError(f"Invalid STT engine: {engine_name}")

    try:
        engine = engine_class(api_key, language_code)
        return engine.recognize(audio)
    except Exception as e:
        print(f"Failed to recognize speech with {engine_name} engine: {e}")
        raise e
