from google.cloud import speech_v1p1beta1 as speech

client = speech.SpeechClient()


def speect_to_text(audio_file, language_code):
    audio = speech.RecognitionAudio(content=audio_file)
    language_code = language_code + "-IN"
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language_code,
    )

    response = client.recognize(config=config, audio=audio)

    return response.results[0].alternatives[0].transcript
