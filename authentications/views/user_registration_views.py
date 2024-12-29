import jwt
import pyotp
from cryptography import fernet
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework import (
    decorators,
    exceptions,
    permissions,
    response,
    status,
    viewsets,
)
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken

from authentications import serializers
from authentications.models import User
from authentications.views.common_functions import (
    direct_login,
    generate_link,
    generate_otp,
    get_origin,
    get_token,
    send_otp,
    send_verification_email,
)
from utils.extensions.permissions import IsAuthenticatedAndEmailNotVerified
from utils.helper import decode_token, decrypt


class RegistrationView(viewsets.GenericViewSet):
    """
    New User Create View
    """

    serializer_class = serializers.RegistrationSerializer
    queryset = User.objects.all()
    permission_classes = ()
    authentication_classes = ()

    @decorators.action(
        detail=False,
        url_path="verify-identity",
        methods=["post"],
        serializer_class=serializers.VerifyIdentitySerializer,
    )
    def verify_identity(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        otp, secret = generate_otp()
        body = f"""
안녕하세요.

팔레트샵을 이용해 주셔서 진심으로 감사드립니다. 세상의 아름다운 원단들의 매력을 마음껏 즐기시길 바랍니다. 

인증번호 : {otp}
위 인증번호를 입력하여 회원가입을 완료해주세요.

감사합니다.
"""
        subject = "[Falette Shop] 이메일 인증번호 요청 안내입니다."
        return send_otp(email, otp, secret, subject, body)

    @decorators.action(
        detail=False,
        url_path="verify-otp",
        methods=["post"],
        serializer_class=serializers.VerifyOTPSerializer,
    )
    def verify_otp(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.data.get("email")
            secret = serializer.data.get("secret")
            otp = serializer.data.get("otp")

            try:
                user = self.queryset.get(email=email)
                # user_serializer = serializers.UserSerializer(user)
            except:
                user = None

            totp = pyotp.TOTP(secret, interval=300)
            print(totp)

            if totp.verify(otp):
                if user:
                    user.is_verified = True
                    user.save()
                    return Response(
                        {
                            "message": "이메일이 확인되었습니다.",
                            "data": {
                                "name": user.user_information.full_name,
                                "email": user.email,
                                "is_verified": True,
                            },
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            "message": "이메일이 확인되었습니다.",
                            "data": {"name": None, "email": email, "is_verified": True},
                        },
                        status=status.HTTP_200_OK,
                    )
            else:
                print("out", totp)
                raise exceptions.ValidationError(
                    {
                        "detail": "인증번호가 맞지 않습니다.",
                        "data": {"is_verified": False},
                    }
                )
        return Response(
            {"message": "문제가 발생했습니다. 다시 시도하세요.", "is_verified": False},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def _login(self, user, message: str):
        token = get_token(user)
        resp = direct_login(
            request=self.request,
            user=user,
            token_data={
                settings.REST_AUTH.get("JWT_AUTH_REFRESH_COOKIE", "refresh"): str(
                    token
                ),
                settings.REST_AUTH.get("JWT_AUTH_COOKIE", "access"): str(
                    token.access_token
                ),
            },
        )

        resp.data["detail"] = _("회원가입이 완료되었습니다")
        return resp

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            get_user = User.objects.get(email=request.data.get("email"))
            return Response(
                {"message": "해당 이메일은 가입 된 이메일입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            return self._login(user, _("회원가입이 완료되었습니다."))
