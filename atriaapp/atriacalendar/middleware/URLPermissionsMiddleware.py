import re

from django.conf import settings
from django.core.exceptions import PermissionDenied


class URLPermissionsMiddleware:
    """
    Simple permissions middleware that checks permissions against URL regexes
    according to settings.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self.request_allowed(request):
            return self.get_response(request)
        else:
            raise PermissionDenied

    def request_allowed(self, request):
        user = request.user
        path = request.path
        url_permissions = getattr(settings, 'URL_PERMISSIONS', [])

        if user.is_anonymous:
            return True

        for url in url_permissions:
            pattern, roles = url

            if re.match(pattern, path):
                for role in roles:
                    if user.has_role(role):
                        return True

                return False

        return True
