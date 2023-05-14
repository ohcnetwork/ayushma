from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()

language_code_voice_map = {
    "bn-IN": "bn-IN-Wavenet-A",
    "en-US": "en-US-Neural2-C",
    "gu-IN": "gu-IN-Wavenet-A",
    "hi-IN": "hi-IN-Neural2-D",
    "kn-IN": "kn-IN-Wavenet-A",
    "ml-IN": "ml-IN-Wavenet-C",
    "mr-IN": "mr-IN-Wavenet-C",
    "pa-IN": "pa-IN-Wavenet-C",
    "ta-IN": "ta-IN-Wavenet-C",
    "te-IN": "te-IN-Standard-A",
}


def text_to_speech(text, language_code):
    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code, name=language_code_voice_map[language_code]
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # The response's audio_content is binary.
    with open("output.mp3", "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')
