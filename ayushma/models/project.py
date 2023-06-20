from django.db import models

from ayushma.models.users import User
from utils.models.base import BaseModel

STT_ENGINE_CHOICES = [
    ("google", "Google"),
    ("whisper", "Whisper"),
]


class Project(BaseModel):
    title = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.PROTECT)
    prompt = models.TextField(default="")
    stt_engine = models.CharField(
        max_length=50, default="whisper", choices=STT_ENGINE_CHOICES
    )
    is_default = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.title} by {self.creator.username}{' (default)' if self.is_default else ''}"
