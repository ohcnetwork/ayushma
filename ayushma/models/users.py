from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

def reverse_choices(choices):
    output = {}
    for choice in choices:
        output[choice[0]] = choice[1]
    return output

class UserManager(BaseUserManager):
    pass


class User(AbstractUser):
    first_name = None
    last_name = None

    external_id = models.UUIDField(default=uuid4, unique=True, db_index=True)

    full_name = models.CharField(max_length=80, blank=True)
    email = models.EmailField(_("email address"), unique=True, db_index=True)

    # User is allowed only chat access, supervisor - can manage projects, admin - can manage everything (incl. users)
    TYPE_VALUE_MAP = {
        "User": 1,
        "Supervisor": 2,
        "Admin": 3
    }

    TYPE_CHOICES = [(value, name) for name, value in TYPE_VALUE_MAP.items()]

    REVERSE_TYPE_MAP = reverse_choices(TYPE_CHOICES)

    user_type = models.IntegerField(choices=TYPE_CHOICES, blank=False)

    last_login_platform = models.CharField(max_length=100, blank=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)

    modified_at = models.DateTimeField(auto_now=True)

    allow_key = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        return request.user.is_superuser or self == request.user or (int(request.data["user_type"]) > 1)

    @staticmethod
    def has_write_permission(request):
        try:
            return int(request.data["user_type"]) == 3 or request.user.is_staff
        except KeyError:
            # No user_type passed, the view shall raise a 400
            return True

    def has_object_write_permission(self, request):
        return self.has_write_permission(self, request)

    def has_object_update_permission(self, request):
        return self.has_write_permission(self, request)

    @staticmethod
    def has_add_user_permission(request):
        return request.user.is_superuser or int(request.data["user_type"]) == 3

    @staticmethod
    def check_username_exists(username):
        return User.objects.get_entire_queryset().filter(username=username).exists()

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.save()