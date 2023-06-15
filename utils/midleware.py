import contextlib
import zoneinfo

from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        with contextlib.suppress(AttributeError):
            timezone.activate(zoneinfo.ZoneInfo(request.user.timezone))
        return self.get_response(request)
