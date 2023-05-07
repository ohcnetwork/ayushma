from django.db import models

from ayushma.models.users import User
from utils.models.base import BaseModel

from .project import Project


class Document(BaseModel):
    title = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to="documents/")
    project = models.ForeignKey(Project, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.title} in {self.project.title}"
