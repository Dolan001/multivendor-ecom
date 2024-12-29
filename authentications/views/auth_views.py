import contextlib
from typing import Any

from dj_rest_auth.jwt_auth import (
    set_jwt_access_cookie,
    set_jwt_refresh_cookie,
    unset_jwt_cookies,
)
from django.conf import settings
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import OpenApiParameter, extend_schema
from pyotp import TOTP
from rest_framework import exceptions, generics, permissions, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from authentications.models import User
from authentications.serializers import (
    LoginSerializer,
    OTPLoginSerializer,
    OTPSerializer,
)
from core.settings import PROJECT_NAME
from utils.extensions import validate_query_params
from utils.extensions.permissions import IsAuthenticatedAndEmailVerified

from .common_functions import (
    direct_login,
    generate_and_send_otp,
    generate_token,
    get_token,
)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: User = serializer.validated_data[1]
        user.is_verified = True
        user.save()
        return direct_login(request, user, serializer.validated_data[0])


class MyTokenRefreshView(generics.GenericAPIView):
    """
    View for get new access token for a valid refresh token
    """

    serializer_class = TokenRefreshSerializer
    permission_classes = ()
    authentication_classes = ()

    @staticmethod
    def _set_cookie(resp, serializer):
        if refresh := serializer.validated_data.get(
            settings.REST_AUTH.get("JWT_AUTH_REFRESH_COOKIE")
        ):  # noqa
            set_jwt_refresh_cookie(
                response=resp,
                refresh_token=refresh,
            )
        set_jwt_access_cookie(
            response=resp,
            access_token=serializer.validated_data.get(
                settings.REST_AUTH.get("JWT_AUTH_COOKIE")
            ),  # noqa
        )

    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get(
            settings.REST_AUTH.get("JWT_AUTH_REFRESH_COOKIE")
        ) or request.data.get(settings.REST_AUTH.get("JWT_AUTH_REFRESH_COOKIE"))

        serializer = self.serializer_class(
            data={settings.REST_AUTH.get("JWT_AUTH_REFRESH_COOKIE"): refresh}
        )
        serializer.is_valid(raise_exception=True)
        resp = Response()
        self._set_cookie(resp=resp, serializer=serializer)
        resp.data = serializer.validated_data
        resp.status_code = status.HTTP_200_OK
        return resp


class LogoutView(views.APIView):
    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.

    Accepts/Returns nothing.
    """

    permission_classes = (permissions.IsAuthenticated,)
    throttle_scope = "dj_rest_auth"

    def get(self, request, *args, **kwargs):
        if getattr(settings, "ACCOUNT_LOGOUT_ON_GET", False):
            resp = self._logout(request)
        else:
            resp = self.http_method_not_allowed(request, *args, **kwargs)

        return self.finalize_response(request, resp, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self._logout(request)

    @staticmethod
    def _logout(request):
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


class OTPLoginView(generics.GenericAPIView):
    serializer_class = OTPLoginSerializer
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user

        token = get_token(user)
        return direct_login(
            request,
            user,
            {
                settings.REST_AUTH.get("JWT_AUTH_REFRESH_COOKIE", "refresh"): str(
                    token
                ),
                settings.REST_AUTH.get("JWT_AUTH_COOKIE", "access"): str(
                    token.access_token
                ),
            },
        )


class OTPCheckView(views.APIView):
    """
    Check if OTP is active for user or not
    """

    permission_classes = (IsAuthenticatedAndEmailVerified,)

    def get(self, request, *args, **kwargs):
        try:
            return Response(
                {
                    "data": [self.request.user.user_two_step_verification.is_active],
                    "detail": self.request.user.user_two_step_verification.is_active,
                }
            )
        except Exception as e:
            raise exceptions.APIException from e


class OTPView(generics.GenericAPIView):
    """
    Get method for OTP Create
    Post method for OTP verify
    Delete method for Disabling OTP
    """

    permission_classes = (IsAuthenticatedAndEmailVerified,)

    # serializer_class = serializers.OTPCreateSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OTPSerializer

    @staticmethod
    def _clear_user_otp(user_otp):
        user_otp.is_active = False
        user_otp.otp_method = "___"
        user_otp.save(update_fields=["is_active", "otp_method"])

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "otp_method",
                type={"type": "string"},
                enum=["authenticator_app", "email", "sms"],
                default="authenticator_app",
                style="form",
                explode=False,
                required=True,
            )
        ]
    )
    @validate_query_params("otp_method", ["authenticator_app", "email", "sms"])
    def get(self, request, *args, **kwargs):
        if (
            otp_method := request.query_params.get("otp_method", "authenticator_app")
        ) == "authenticator_app":
            otp = TOTP(self.request.user.user_two_step_verification.secret_key)
            return Response(
                {
                    "data": {
                        "qr_code": otp.provisioning_uri(
                            self.request.user.email, issuer_name=PROJECT_NAME
                        ),
                        "otp_method": otp_method,
                    },
                    "message": "QR Code is generated",
                }
            )
        else:
            return generate_and_send_otp(self.request.user, otp_method)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user_otp = self.request.user.user_two_step_verification

        if not serializer.is_valid():
            self._clear_user_otp(user_otp)
            raise exceptions.ValidationError(serializer.errors)

        user_otp.is_active = True
        user_otp.otp_method = serializer.validated_data.get("otp_method")
        user_otp.save(update_fields=["is_active", "otp_method"])
        return Response(
            {
                "data": {"detail": "OTP is activated"},
                "message": "OTP is activated",
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        user_otp = self.request.user.user_two_step_verification
        self._clear_user_otp(user_otp)
        return Response({"data": {"detail": "OTP Removed"}, "message": "OTP Removed"})
