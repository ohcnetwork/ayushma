from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from ayushma.token import RandomStringTokenGenerator
from utils.models.base import BaseModel


class ResetPasswordToken(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="password_reset_tokens",
        on_delete=models.CASCADE,
        verbose_name=_(
            "The User which is associated to this password reset token"
        ),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("When was this token generated")
    )
    key = models.CharField(_("Key"), max_length=64, db_index=True, unique=True)
    ip_address = models.GenericIPAddressField(
        _("The IP address of this session"),
        default="",
        blank=True,
        null=True,
    )
    user_agent = models.CharField(
        max_length=256,
        verbose_name=_("HTTP User Agent"),
        default="",
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ResetPasswordToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset token for user {user}".format(user=self.user)

    @staticmethod
    def generate_key():
        return RandomStringTokenGenerator().generate()
