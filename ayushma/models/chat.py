from django.db import models

from ayushma.models.enums import ChatMessageType
from ayushma.models.project import Project
from ayushma.models.users import User
from utils.models.base import BaseModel
from ayushma.models.document import Document


class Chat(BaseModel):
    title = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    language = models.CharField(max_length=10, blank=False, default="en")

    def __str__(self) -> str:
        return f"{self.title} from {self.user.username}"


class ChatMessage(BaseModel):
    chat = models.ForeignKey(Chat, on_delete=models.PROTECT)
    messageType = models.IntegerField(
        choices=ChatMessageType.choices, default=ChatMessageType.USER
    )
    message = models.TextField()
    reference_documents = models.ManyToManyField(Document, blank=True)
    ayushma_audio_url = models.URLField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.message} : {self.chat}"
