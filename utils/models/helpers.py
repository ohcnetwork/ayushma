import re

from utils.helpers import get_random_string


def unique_slugify(instance, text: str, length: int = 0) -> str:
    if not length:
        length = min(50, len(text))

    model = instance.__class__
    slug = re.sub(r"[^\w]+", "-", text)
    slug = slug[: length - 1] if slug[length - 1] == "-" else slug[:length]
    unique_slug = f"{slug}-{get_random_string(8)}"
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = f"{slug}-{get_random_string(8)}"
    return unique_slug


def get_random_slug(instance, length: int) -> str:

    model = instance.__class__
    unique_slug = get_random_string(length)
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = get_random_slug(length)
    return unique_slug
