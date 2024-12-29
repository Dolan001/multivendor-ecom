import contextlib

from dj_rest_auth.jwt_auth import unset_jwt_cookies
from django.conf import settings
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions, response, status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


def user_logout(request):
    with contextlib.suppress(AttributeError, ObjectDoesNotExist):
        request.user.auth_token.delete()

    if settings.REST_AUTH.get("SESSION_LOGIN", False):
        logout(request)

    resp = Response(
        {"detail": "Successfully logged out."},
        status=status.HTTP_200_OK,
    )

    if settings.REST_AUTH.get("USE_JWT", True):
        cookie_name = settings.REST_AUTH.get("JWT_AUTH_COOKIE", "access")

        unset_jwt_cookies(resp)

        if "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS:
            # add refresh token to blacklist
            try:
                token = RefreshToken(
                    request.COOKIES.get(
                        settings.REST_AUTH.get("JWT_AUTH_REFRESH_COOKIE")
                    )
                    or request.data.get(
                        settings.REST_AUTH.get("JWT_AUTH_REFRESH_COOKIE")
                    )
                )
                token.blacklist()
            except KeyError:
                resp.data = {
                    "detail": "Refresh token was not included in request data."
                }
                resp.status_code = status.HTTP_401_UNAUTHORIZED
            except (TokenError, AttributeError, TypeError) as error:
                if hasattr(error, "args"):
                    if (
                        "Token is blacklisted" in error.args
                        or "Token is invalid or expired" in error.args
                    ):
                        resp.data = {"detail": error.args[0]}
                        resp.status_code = status.HTTP_401_UNAUTHORIZED
                    else:
                        resp.data = {"detail": "An error has occurred."}
                        resp.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

                else:
                    resp.data = {"detail": "An error has occurred."}
                    resp.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        elif not cookie_name:
            message = (
                "Neither cookies or blacklist are enabled, so the token "
                "has not been deleted server side. "
                "Please make sure the token is deleted client side.",
            )
            resp.data = {"detail": message}
            resp.status_code = status.HTTP_200_OK
    return resp
