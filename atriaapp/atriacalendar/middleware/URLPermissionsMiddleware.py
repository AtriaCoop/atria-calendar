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
        url_permissions = getattr(settings, 'URL_NAMESPACE_PERMISSIONS', [])

        if user.is_anonymous:
            return True

        url_namespace = request.session.get('URL_NAMESPACE')

        if url_namespace is None:
            return False

        url_namespace = url_namespace.replace(':', '')

        if url_namespace in path:

            if user.is_staff:
                return True

            allowed_roles = url_permissions.get(url_namespace, ())

            for role in allowed_roles:
                if user.has_role(role):
                    return True

        return False
