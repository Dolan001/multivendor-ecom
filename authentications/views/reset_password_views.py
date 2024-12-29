import pyotp
from django.utils.translation import gettext as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import exceptions, generics, status
from rest_framework.response import Response

from authentications import serializers
from authentications.models import User
from authentications.views.common_functions import (
    generate_and_send_otp,
    generate_link,
    generate_otp,
    generate_token,
    get_origin,
    send_otp,
    send_verification_email,
)
from utils import helper
from utils.extensions import validate_query_params


# ============***********============
# Password reset views
# ============***********============
class ResetPasswordEmailCheckView(generics.GenericAPIView):
    """
    View for getting email or sms for password reset
    post: email: ""
    """

    serializer_class = serializers.ResetPasswordEmailCheckSerializer
    authentication_classes = []
    permission_classes = []

    # throttle_classes = (AnonUserRateThrottle,)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user

        if not user:
            return Response(
                {"message": "Email is not verified", "data": {"is_verified": False}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"message": "Email is verified", "data": {"is_verified": True}},
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(generics.GenericAPIView):
    """
    View for getting email or sms for password reset
    post: email: ""
    """

    serializer_class = serializers.ResetPasswordSerializer
    authentication_classes = []
    permission_classes = []

    # throttle_classes = (AnonUserRateThrottle,)

    @staticmethod
    def email_sender_helper(user):
        otp, secret = generate_otp()
        subject = "[Falette Shop] 비밀번호 재설정 인증번호 안내입니다."
        body = f"""
안녕하세요.

팔레트샵에서 비밀번호 재설정을 요청하셨습니다. 아래 인증번호를 입력하여 비밀번호를 재설정해주세요. 인증번호는 일정 시간 동안만 유효하니 유효기간 내에 사용하시기 바랍니다.

인증번호: {otp}

만약 비밀번호 재설정을 요청하지 않으셨다면 이 이메일을 무시하셔도 됩니다.

감사합니다.
"""
        return send_otp(user.email, otp, secret, subject, body)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user

        if not user.email:
            raise exceptions.PermissionDenied(detail="No Email found!!!")
        return self.email_sender_helper(user)


class ResetPasswordCheckView(generics.GenericAPIView):
    """
    View for checking if the url is expired or not
    post: token: ""
    """

    authentication_classes = []
    permission_classes = []
    serializer_class = serializers.ResetPasswordCheckSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)

        if serializer.is_valid():
            email = serializer.data.get("email")
            secret = serializer.data.get("secret")
            otp = serializer.data.get("otp")

            try:
                user = User.objects.get(email=email)
                totp = pyotp.TOTP(secret, interval=300)
                print(totp)

                if totp.verify(otp):
                    print("Verified")
                    secret = generate_token(user)
                    print(secret)
                    return Response(
                        {
                            "message": "이메일이 확인되었습니다.",
                            "data": {
                                "secret": secret,
                                "is_verified": True,
                            },
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"message": "인증번호가 맞지 않습니다.", "is_verified": False},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except:
                return Response(
                    {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )

        return Response(
            {"message": "문제가 발생했습니다. 다시 시도하세요.", "is_verified": False},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ResetPasswordConfirmView(generics.GenericAPIView):
    """
    View for resetting password after checking the token
    post: secret: "", password: ""
    """

    serializer_class = serializers.ResetPasswordConfirmSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        return self._change_password(serializer)

    @staticmethod
    def _change_password(serializer):
        user = serializer.user
        user.set_password(serializer.validated_data.get("password"))
        user.save(update_fields=["password"])
        return Response({"detail": _("Password Changed Successfully")})
