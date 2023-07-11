from django.db.models import IntegerChoices


class ChatMessageType(IntegerChoices):
    USER = 1
    SYSTEM = 2
    AYUSHMA = 3


class DocumentType(IntegerChoices):
    FILE = 1
    URL = 2
    TEXT = 3


class STTEngine(IntegerChoices):
    WHISPER = 1
    GOOGLE = 2


class FeedBackRating(IntegerChoices):
    HALLUCINATING = 1
    WRONG = 2
    UNSATISFACTORY = 3
    SATISFACTORY = 4
    GOOD = 5
    EXCELLENT = 6


class ModelType(IntegerChoices):
    GPT_3_5 = 1
    GPT_3_5_16K = 2
    GPT_4 = 3
    GPT_4_32K = 4
