from django.db import models

from ayushma.models.enums import ModelType, STTEngine
from ayushma.models.users import User
from utils.models.base import BaseModel


class Project(BaseModel):
    title = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.PROTECT)
    prompt = models.TextField(default="")
    stt_engine = models.IntegerField(
        choices=STTEngine.choices, default=STTEngine.WHISPER
    )
    model = models.IntegerField(choices=ModelType.choices, default=ModelType.GPT_3_5)
    is_default = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.title} by {self.creator.username}{' (default)' if self.is_default else ''}"
