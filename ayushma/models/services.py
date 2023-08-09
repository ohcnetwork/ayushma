import secrets
import time

from django.db import models
from django.utils import timezone

from ayushma.models.users import User
from utils.models.base import BaseModel


class Service(BaseModel):
    name = models.CharField(max_length=100)
    allow_key = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return self.name


class APIKey(BaseModel):
    title = models.CharField(max_length=50)
    key = models.CharField(max_length=50)
    creator = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True
    )  # deprecated
    service = models.ForeignKey(
        Service, on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self) -> str:
        return f"{self.title}"


class TempToken(BaseModel):
    token = models.CharField(max_length=256)
    api_key = models.ForeignKey(APIKey, on_delete=models.PROTECT)
    ip = models.CharField(max_length=100)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.token} for {self.api_key.service.name}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.token = self.token = "tt-" + secrets.token_urlsafe(128)
            self.expires_at = timezone.now() + timezone.timedelta(days=31)
        return super().save(*args, **kwargs)
