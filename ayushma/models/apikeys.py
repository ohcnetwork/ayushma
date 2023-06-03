from django.db import models

from ayushma.models.users import User
from utils.models.base import BaseModel


class APIKey(BaseModel):
    title = models.CharField(max_length=50)
    key = models.CharField(max_length=50)
    creator = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.title} by {self.creator.username}"
