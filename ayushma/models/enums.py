from django.db.models import IntegerChoices


class ChatMessageType(IntegerChoices):
    USER = 1
    SYSTEM = 2
    AYUSHMA = 3

class DocumentType(IntegerChoices):
    FILE = 1
    URL = 2
    TEXT = 3