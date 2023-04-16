import re
from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    pass


class User(AbstractUser):
    first_name = None
    last_name = None

    external_id = models.UUIDField(default=uuid4, unique=True, db_index=True)

    full_name = models.CharField(max_length=80, blank=True)
    email = models.EmailField(_("email address"), unique=True, db_index=True)

    last_login_platform = models.CharField(max_length=100, blank=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)

    modified_at = models.DateTimeField(auto_now=True)

    allow_key = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()
