from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import SimpleLazyObject
from publication_backbone.utils.auth import basic_auth

#---------------------------------
import logging
from django.conf import settings
logger = logging.getLogger(settings.PROJECT_NAME)
#---------------------------------


def get_user(request):
    if not hasattr(request, '_cached_http_auth_user'):
        request._cached_http_auth_user = basic_auth(request)
    return request._cached_http_auth_user



class HTTPAuthRemoteUserMiddleware(object):
    """
    Middleware for utilizing Web-server-provided authentication.

    If request.user is not authenticated, then this middleware attempts to
    authenticate the username passed in the ``HTTP_AUTHORIZATION`` request header.
    If authentication is successful, the user is automatically logged in to
    persist the user in the session.

    The header used is configurable and defaults to ``HTTP_AUTHORIZATION``.  Subclass
    this class and change the ``header`` attribute if you need to use a
    different header.
    """

    # Name of request header to grab username from.  This will be the key as
    # used in the request.META dictionary, i.e. the normalization of headers to
    # all uppercase and the addition of "HTTP_" prefix apply.
    header = "HTTP_AUTHORIZATION"

    def process_request(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the HTTPAuthRemoteUserMiddleware class.")

        if not self.header in request.META:
            return

        # If the user is already authenticated and that user is the user we are
        # getting passed in the headers, then the correct user is already
        # persisted in the session and we don't need to continue.

        user = SimpleLazyObject(lambda: get_user(request))

        if user:
            # User is valid.  Set request.user and persist user in the session
            # by logging the user in.
            request.user = user
            auth.login(request, user)
