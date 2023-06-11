from django.db import models

from ayushma.models.enums import DocumentType
from ayushma.models.project import Project
from utils.models.base import BaseModel


class Document(BaseModel):
    title = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    document_type = models.IntegerField(
        choices=DocumentType.choices, default=DocumentType.FILE
    )
    file = models.FileField(null=True, blank=True)
    text_content = models.TextField(null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.title} in {self.project.title}"
