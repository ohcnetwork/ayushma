from django.db import models

from ayushma.models.enums import ChatMessageType
from ayushma.models.users import User
from utils.models.base import BaseModel


class Chat(BaseModel):
    title = models.CharField(max_length=30)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.title} from {self.user.username}"


class ChatMessage(BaseModel):
    chat = models.ForeignKey(Chat, on_delete=models.PROTECT)
    messageType = models.IntegerField(
        choices=ChatMessageType.choices, default=ChatMessageType.USER
    )
    message = models.TextField()

    def __str__(self) -> str:
        return f"{self.chat.title} - {self.user.username}"
