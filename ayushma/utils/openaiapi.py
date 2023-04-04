import openai
from django.conf import settings


def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    openai.api_key = settings.OPENAI_API_KEY
    return openai.Embedding.create(input=[text], model=model)["data"][0]["embedding"]
