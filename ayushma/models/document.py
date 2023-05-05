from django.db import models

from utils.models.base import BaseModel

from .project import Project


class Document(BaseModel):
    FILE = "file"
    URL = "url"
    TEXT = "text"
    DOCUMENT_TYPE_CHOICES = (
        (FILE, "File"),
        (URL, "URL"),
        (TEXT, "Text"),
    )

    title = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    document_type = models.CharField(max_length=4, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to="documents/", null=True, blank=True)
    text_content = models.TextField(null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.title} in {self.project.title}"
