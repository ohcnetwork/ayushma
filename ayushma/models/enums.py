from django.db.models import IntegerChoices


class ChatMessageType(IntegerChoices):
    USER = 1
    SYSTEM = 2
    AYUSHMA = 3
