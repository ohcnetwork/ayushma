import random
import string


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
