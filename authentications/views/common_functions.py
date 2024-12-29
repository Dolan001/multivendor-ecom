import datetime
import random
from typing import Literal

import pyotp
from dj_rest_auth.jwt_auth import set_jwt_cookies
from django.conf import settings
from django.contrib.auth import login
from django.utils.translation import gettext as _
from pyotp import TOTP
from rest_framework import exceptions, response, status
from rest_framework_simplejwt.tokens import RefreshToken

from authentications.models import User
from authentications.serializers import UserDetailsSerializer
from utils.helper import encode_token, encrypt
from utils.modules import EmailSender
from utils.modules.solapi_sms import SolApiClient


def get_origin(self):
    try:
        return self.request.headers["origin"]
    except Exception as e:
        raise exceptions.PermissionDenied(
            detail=_("Origin not found on request header")
        ) from e


def direct_login(request, user: User, token_data):
    if settings.REST_AUTH.get("SESSION_LOGIN", False):
        user.backend = "your_project.authentication_backend.CustomBackend"
        login(request, user)

    resp = response.Response()

    set_jwt_cookies(
        response=resp,
        access_token=token_data.get(
            settings.REST_AUTH.get("JWT_AUTH_COOKIE", "access"),
        ),
        refresh_token=token_data.get(
            settings.REST_AUTH.get("JWT_AUTH_REFRESH_COOKIE", "refresh"),
        ),
    )
    data = {
        "token_data": token_data,
        "user_data": UserDetailsSerializer(user, context={"request": request}).data,
    }
    resp.data = {"data": data}
    resp.status_code = status.HTTP_200_OK
    return resp


def generate_and_send_otp(
    user: User,
    otp_method: Literal["sms", "email"],
    generate_secret: bool = False,
    **kwargs,
):
    otp = TOTP(
        user.user_two_step_verification.secret_key,
        interval=settings.TOKEN_TIMEOUT_SECONDS,
    )

    otp_code = otp.now()
    if otp_method == "sms":
        # sms send for otp code
        send_verification_sms(user.user_information.phone_number, otp_code)
    elif otp_method == "email":
        # email send for otp code
        send_otp_email(user, otp_code)

    return response.Response(
        {
            "data": {
                "secret": generate_token(user, **kwargs) if generate_secret else None,
                "otp_method": otp_method,
                "detail": _(
                    f"OTP is active for {settings.TOKEN_TIMEOUT_SECONDS} seconds"
                ),
            },
            "message": _("OTP is Sent"),
        },
        status=status.HTTP_200_OK,
    )


def generate_link(user: User, origin: str, route: str, **kwargs) -> str:
    return f"{origin}/auth/{route}/{generate_token(user, **kwargs)}/"


def generate_token(user: User, **kwargs):
    payload = {
        "user": str(user.id),
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(seconds=settings.TOKEN_TIMEOUT_SECONDS),
    }
    token = encrypt(encode_token(payload=payload)).decode()
    return token


def send_otp_email(email, otp, subject=None, body=None):
    if not subject:
        subject = "[Falette Shop] OTP verification"
    if not body:
        body = f"One time verification code is {otp}"

    print(subject)
    print(body)

    email = EmailSender(send_to=[email], subject=subject, body=body)
    email.send_email()


def send_verification_email(user, link):
    body = f"Your Verification is {link}"
    subject = "[Falette Shop] 이메일 인증번호 요청 안내입니다."
    email = EmailSender(send_to=[user.email], subject=subject, body=body)
    email.send_email()


def send_verification_sms(phone_number, code):
    # body = f"One time verification code is {code}"
    body = f"""
    안녕하세요.

    팔레트샵을 이용해 주셔서 진심으로 감사드립니다. 세상의 아름다운 원단들의 매력을 마음껏 즐기시길 바랍니다. 

    인증번호 : {code}
    위 인증번호를 입력하여 회원가입을 완료해주세요.

    감사합니다.
    """
    solapi = SolApiClient()
    solapi.send_one(phone_number, body)
    # solapi.get_balance()
    print(body)


def extract_token(refresh_token: RefreshToken) -> dict:
    return {
        settings.REST_AUTH.get("JWT_AUTH_REFRESH_COOKIE", "refresh"): str(
            refresh_token
        ),
        settings.REST_AUTH.get("JWT_AUTH_COOKIE", "access"): str(
            refresh_token.access_token
        ),
    }


def get_token(user):
    token = RefreshToken.for_user(user)
    token["email"] = user.email
    token["is_staff"] = user.is_staff
    token["is_active"] = user.is_active
    token["is_superuser"] = user.is_superuser
    return token


def generate_otp():
    secret = pyotp.random_base32()
    otp = TOTP(secret, interval=300)
    otp_code = otp.now()
    return otp_code, secret


def send_otp(email, otp_code, secret, subject=None, body=None):
    try:
        send_otp_email(email, otp_code, subject, body)
        return response.Response(
            {
                "data": {
                    "email": email,
                    "secret": secret,
                    "detail": "OTP는 5분 동안 활성화됩니다.",
                },
                "message": "번호를 보냈습니다.",
            },
            status=status.HTTP_200_OK,
        )
    except:
        return response.Response(
            {
                "data": {
                    "otp": otp_code,
                    "email": email,
                    "secret": secret,
                    "detail": "OTP는 5분 동안 활성화됩니다.",
                },
                "message": "번호를 보냈습니다.",
            },
            status=status.HTTP_200_OK,
        )
