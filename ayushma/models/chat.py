from django.db import models

from ayushma.models.apikeys import APIKey
from ayushma.models.document import Document
from ayushma.models.enums import ChatMessageType
from ayushma.models.project import Project
from ayushma.models.users import User
from utils.models.base import BaseModel


class Chat(BaseModel):
    title = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, blank=True, null=True
    )
    prompt = models.TextField(blank=True, null=True)
    api_key = models.ForeignKey(APIKey, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.title} from {self.user.username if self.user else self.api_key.creator.username}"


class ChatMessage(BaseModel):
    chat = models.ForeignKey(Chat, on_delete=models.PROTECT)
    messageType = models.IntegerField(
        choices=ChatMessageType.choices, default=ChatMessageType.USER
    )
    message = models.TextField()
    original_message = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=10, blank=False, default="en")
    reference_documents = models.ManyToManyField(Document, blank=True)
    audio = models.FileField(blank=True, null=True)
    meta = models.JSONField(blank=True, null=True)
    temperature = models.FloatField(blank=True, null=True)
    top_k = models.IntegerField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.message} : {self.chat}"


class ChatFeedback(BaseModel):
    chat_message = models.ForeignKey(ChatMessage, on_delete=models.PROTECT)
    liked = models.BooleanField()
    message = models.TextField(blank=True, null=True)
