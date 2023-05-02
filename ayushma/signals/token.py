from django.core.mail import EmailMessage
from django.dispatch import Signal, receiver
from django.template.loader import render_to_string
from django.conf import settings

reset_password_token_created = Signal()


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, reset_password_token, *args, **kwargs
):
    context = {
        "username": reset_password_token.user.username,
        "reset_password_url": "{}/reset-password?token={}&user_id={}".format(
            settings.CURRENT_DOMAIN,
            reset_password_token.key,
            reset_password_token.user.external_id,
        ),
        "support_email": settings.SUPPORT_EMAIL,
    }

    email_message = render_to_string("email/reset_password.html", context)
    msg = EmailMessage(
        "Password Reset for Ayushma",
        email_message,
        settings.DEFAULT_FROM_EMAIL,
        (reset_password_token.user.email,),
    )
    msg.content_subtype = "html"
    msg.send()
