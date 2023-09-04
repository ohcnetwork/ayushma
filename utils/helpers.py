import random
import string

import requests
from django.conf import settings


def get_random_string(length: int) -> str:
    return "".join(random.choices(string.hexdigits, k=length))


def get_unique_id(length: int) -> str:
    return "".join(
        random.choices(
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-",
            k=length,
        )
    )


def get_client_ip(request):
    if x_forwarded_for := request.META.get("HTTP_X_FORWARDED_FOR"):
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
        return x_forwarded_for.split(",")[0].strip()
    else:
        return request.META.get("REMOTE_ADDR")


def validatecaptcha(recaptcha_response):
    if not getattr(settings, "GOOGLE_RECAPTCHA_SECRET_KEY", None):
        return True

    if not recaptcha_response:
        return False
    values = {
        "secret": settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        "response": recaptcha_response,
    }
    captcha_response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify", data=values
    )
    result = captcha_response.json()

    return result.get("success", False)
