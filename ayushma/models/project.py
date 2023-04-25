from django.db import models

from ayushma.models.users import User
from utils.models.base import BaseModel


class Project(BaseModel):
    title = models.CharField(max_length=50)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.title} from {self.user.username}"
