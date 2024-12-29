from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView

from authentications.views import (  # AppleLoginView,; GoogleLoginView,
    ChangePasswordView,
    KakaoLoginView,
    LoginView,
    LogoutView,
    MyTokenRefreshView,
    OTPCheckView,
    OTPLoginView,
    OTPView,
    PasswordValidateView,
    RegistrationView,
    UserInformationUpdateView,
    UserViews,
)
from authentications.views.reset_password_views import (
    ResetPasswordCheckView,
    ResetPasswordConfirmView,
    ResetPasswordEmailCheckView,
    ResetPasswordView,
)

router = DefaultRouter()
router.register(r"register", RegistrationView, basename="register")

password_urls = [
    path("password-validate/", PasswordValidateView.as_view()),
    path("password-change/", ChangePasswordView.as_view(), name="change_password"),
    # reset password
    path(
        "reset-password/email-validate/",
        ResetPasswordEmailCheckView.as_view(),
        name="email-check",
    ),
    path(
        "reset-password/otp-send/",
        ResetPasswordView.as_view(),
        name="request-password-reset",
    ),
    path(
        "reset-password/otp-verify/",
        ResetPasswordCheckView.as_view(),
        name="password-verify",
    ),
    path("reset-password/set-new-password/", ResetPasswordConfirmView.as_view()),
]
login_urls = [
    path("login/vendor/", LoginView.as_view(), name="vendor-login"),
    path("login/customer/", LoginView.as_view(), name="customer-login"),
    path("login/admin/", LoginView.as_view(), name="admin-login"),
    # path("otp-login/", OTPLoginView.as_view(), name="otp-login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", MyTokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
profile_urls = [
    path(
        "user/profile/<str:id>/",
        UserViews.as_view({"get": "retrieve"}),
        name="user_profile",
    ),
    path(
        "user/my-profile/",
        UserViews.as_view({"get": "profile"}),
        name="my_profile",
    ),
    path(
        "user/update/",
        UserInformationUpdateView.as_view({"patch": "update"}),
        name="update_user",
    ),
    path(
        "user/delete/<str:id>/",
        UserViews.as_view({"delete": "destroy"}),
        name="delete_account",
    ),
]
signup_urls = []
social_urls = [
    # path("google/", GoogleLoginView.as_view()),
    path("kakao/", KakaoLoginView.as_view()),
    # path("apple/", AppleLoginView.as_view()),
]
urlpatterns = []
urlpatterns += router.urls
urlpatterns += login_urls
urlpatterns += profile_urls
urlpatterns += signup_urls
urlpatterns += password_urls
urlpatterns += social_urls
