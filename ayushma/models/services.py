from django.db import models

from ayushma.models.users import User
from utils.models.base import BaseModel


class Service(BaseModel):
    name = models.CharField(max_length=100)
    openapi_key = models.CharField(max_length=100, null=True, blank=True)
    allow_key = models.BooleanField(default=False)
    hostname = models.CharField(max_length=100, null=True, blank=True)


class TempToken(BaseModel):
    token = models.CharField(max_length=100)
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    ip = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.token} for {self.service.name}"


class APIKey(BaseModel):
    title = models.CharField(max_length=50)
    key = models.CharField(max_length=50)
    creator = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.title} by {self.creator.username}"
