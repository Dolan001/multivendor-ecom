import json
import time
from datetime import timedelta

import jwt
import requests
import requests.exceptions
from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from jwt.algorithms import RSAAlgorithm
from rest_framework import exceptions, response, status, views
from social_core.backends.apple import AppleIdAuth
from social_core.backends.google import GoogleOAuth2
from social_core.backends.kakao import KakaoOAuth2
from social_django.utils import load_backend, load_strategy

from authentications.register import register_social_user, save_image_from_url
from authentications.serializers import SocialLoginSerializer, UserDetailsSerializer

from .common_functions import extract_token, get_token


class KakaoLoginView(views.APIView):
    permission_classes = ()
    authentication_classes = ()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "access_token",
                type={"type": "string"},
                style="form",
                explode=False,
                required=True,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        request_data = self.request.query_params
        serializer = SocialLoginSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        strategy = load_strategy(request)
        kakao_backend = KakaoOAuth2(strategy=strategy)
        try:
            user_data = kakao_backend.user_data(
                serializer.validated_data.get("access_token")
            )
        except requests.HTTPError as e:
            raise exceptions.ValidationError(
                {"detail": json.loads(e.response.content).get("msg")}
            )
        try:
            user = register_social_user(
                profile_image_url=user_data.get("kakao_account")
                .get("profile")
                .get("profile_image_url"),
                email=user_data.get("kakao_account").get("email"),
                name=user_data.get("kakao_account").get("profile").get("nickname"),
                provider="kakao",
                role="user",
            )
        except Exception as e:
            return response.Response(
                {"detail": "Something went wrong"}, status=status.HTTP_404_NOT_FOUND
            )
        token_data = extract_token(get_token(user))

        return response.Response(token_data)


# class GoogleLoginView(views.APIView):
#     permission_classes = ()
#     authentication_classes = ()
#
#     @extend_schema(
#         parameters=[
#             OpenApiParameter(
#                 "code",
#                 type={"type": "string"},
#                 style="form",
#                 explode=False,
#                 required=True,
#             )
#         ]
#     )
#     def get(self, request, *args, **kwargs):
#         serializer = SocialLoginSerializer(data=self.request.query_params)
#         serializer.is_valid(raise_exception=True)
#         google_backend = GoogleOAuth2()
#         try:
#             data = {
#                 "code": serializer.validated_data.get("code"),
#                 "client_id": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
#                 "client_secret": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
#                 "redirect_uri": settings.GOOGLE_REDIRECT_URL,
#                 "grant_type": "authorization_code",
#             }
#             resp = requests.post(settings.GOOGLE_TOKEN_URL, data=data)
#
#             print(resp.json())
#
#             user_data = google_backend.user_data(resp.json().get("access_token"))
#             print(user_data)
#
#         except requests.exceptions.HTTPError as e:
#             raise exceptions.AuthenticationFailed(detail=e) from e
#
#         tokens = register_social_user(
#             profile_image_url=user_data.get("picture"),
#             email=user_data.get("email"),
#             name=user_data.get("name"),
#             provider="google",
#         )
#
#         return response.Response(tokens)

# class KakaoLoginView(views.APIView):
#     permission_classes = ()
#     authentication_classes = ()
#
#     @extend_schema(
#         parameters=[
#             OpenApiParameter(
#                 "code",
#                 type={"type": "string"},
#                 style="form",
#                 explode=False,
#                 required=True,
#             ),
#             OpenApiParameter(
#                 "type",
#                 enum=["web", "ios", "android"],
#                 type={"type": "string"},
#                 style="form",
#                 explode=False,
#                 required=True,
#             ),
#         ]
#     )
#     def get(self, request, *args, **kwargs):
#         request_data = self.request.query_params
#         serializer = SocialLoginSerializer(data=request_data)
#         serializer.is_valid(raise_exception=True)
#         strategy = load_strategy(request)
#         kakao_backend = KakaoOAuth2(strategy=strategy)
#         try:
#             if request_data.get("type", "web") == "web":
#                 data = {
#                     "code": serializer.validated_data.get("code"),
#                     "client_id": settings.SOCIAL_AUTH_KAKAO_APP_KEY,
#                     "redirect_uri": settings.KAKAO_REDIRECT_URL,
#                     "grant_type": "authorization_code",
#                 }
#                 resp = requests.post(settings.KAKAO_TOKEN_URL, data=data)
#
#                 user_data = kakao_backend.user_data(resp.json().get("access_token"))
#             else:
#                 user_data = kakao_backend.user_data(
#                     serializer.validated_data.get("code")
#                 )
#
#         except requests.exceptions.HTTPError as e:
#             raise exceptions.AuthenticationFailed(detail=e) from e
#
#         tokens = register_social_user(
#             profile_image_url=user_data.get("kakao_account")
#             .get("profile")
#             .get("profile_image_url"),
#             email=user_data.get("kakao_account").get("email"),
#             name=user_data.get("kakao_account").get("profile").get("nickname"),
#             provider="kakao",
#         )
#
#         return response.Response(tokens)


# class AppleLoginView(views.APIView):
#     permission_classes = ()
#     authentication_classes = ()
#
#     def get_key_and_secret(self, client_id):
#         headers = {"kid": settings.SOCIAL_AUTH_APPLE_ID_KEY}
#         payload = {
#             "iss": settings.SOCIAL_AUTH_APPLE_ID_TEAM,
#             "iat": timezone.now(),
#             "exp": timezone.now() + timedelta(days=180),
#             "aud": "https://appleid.apple.com",
#             "sub": client_id,
#         }
#
#         client_secret = jwt.encode(
#             payload,
#             key=settings.SOCIAL_AUTH_APPLE_ID_SECRET,
#             algorithm="ES256",
#             headers=headers,
#         )
#
#         return client_secret
#
#     def post(self, request, *args, **kwargs):
#         request_data = self.request.data
#         client_type = request_data.get("type", "web")
#         client_id = (
#             settings.SOCIAL_AUTH_APPLE_ID_SERVICE
#             if client_type == "web"
#             else settings.SOCIAL_AUTH_APPLE_ID_CLIENT
#         )
#         serializer = SocialLoginSerializer(data=request_data)
#         serializer.is_valid(raise_exception=True)
#         try:
#             data = {
#                 "code": serializer.validated_data.get("code"),
#                 "client_id": client_id,
#                 "client_secret": self.get_key_and_secret(client_id),
#                 "redirect_uri": settings.APPLE_REDIRECT_URL,
#                 "grant_type": "authorization_code",
#             }
#             resp = requests.post(
#                 settings.APPLE_TOKEN_URL,
#                 data=data,
#                 headers={"content-type": "application/x-www-form-urlencoded"},
#             )
#
#             if resp.status_code == 200:
#                 decoded = jwt.decode(
#                     resp.json().get("id_token"),
#                     audience=client_id,
#                     options={"verify_signature": False},
#                 )
#
#                 user = (
#                     request_data.get("user", {})
#                     if client_type == "web"
#                     else json.loads(request_data.get("user", "{}"))
#                 )
#
#                 full_name = (
#                     (
#                         f"{user.get('name').get('firstName')} {user.get('name').get('lastName')}"
#                     )
#                     if len(user)
#                     else ""
#                 )
#                 email = user.get("email") or decoded.get("email")
#
#                 tokens = register_social_user(
#                     profile_image_url=None,
#                     email=email,
#                     name=full_name,
#                     provider="apple",
#                 )
#                 return response.Response(tokens)
#
#             else:
#                 raise exceptions.AuthenticationFailed(detail=resp.json())
#
#         except requests.exceptions.HTTPError as e:
#             raise exceptions.AuthenticationFailed(detail=e) from e
