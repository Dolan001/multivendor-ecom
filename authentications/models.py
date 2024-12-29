import uuid

from django.contrib.auth.models import AbstractBaseUser, Permission, PermissionsMixin
from django.contrib.contenttypes.models import ContentType
from django.db import models

from authentications.user_manager import UserManager

# ========****************========
# Custom authentications user model
# ========****************========
from core.models import BaseModel, CompressedImageField
# from utils.helper import content_file_path

USER_OAUTH_PROVIDER = (
    ("google", "google"),
    ("apple", "apple"),
    ("kakao", "kakao"),
    ("email", "email"),
)

ROLE = (
        ("admin", "Admin"),
        ("vendor", "Vendor"),
        ("customer", "Customer"),
    )


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model Class
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        verbose_name="ID",
    )
    email = models.EmailField(max_length=100, verbose_name="Email", unique=True)
    oauth_provider = models.CharField(choices=USER_OAUTH_PROVIDER, max_length=10)
    role = models.CharField(choices=ROLE, max_length=10, default="user")
    date_joined = models.DateTimeField(
        verbose_name="Date Joined",
        auto_now_add=True,
    )
    last_login = models.DateTimeField(auto_now=True)

    # user role
    is_superuser = models.BooleanField(
        verbose_name="Superuser Status",
        default=False,
        help_text="Designate if the " "user has superuser " "status",
    )
    is_staff = models.BooleanField(
        verbose_name="Staff Status",
        default=False,
        help_text="Designate if the user has " "staff status",
    )
    is_active = models.BooleanField(
        verbose_name="Active Status",
        default=True,
        help_text="Designate if the user has " "active status",
    )
    is_verified = models.BooleanField(
        verbose_name="Email Verified",
        default=False,
        help_text="Email Verified",
    )
    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = [
    #     "email",
    # ]

    objects = UserManager()

    def __str__(self):
        return self.email


class UserInformation(BaseModel):
    GENDER = (("male", "male"), ("female", "female"), ("other", "other"))
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_information"
    )
    full_name = models.CharField(
        max_length=100, verbose_name="Full Name", blank=True, null=True
    )
    # profile_picture = models.ImageField(
    #     upload_to=content_file_path,
    #     blank=True,
    #     null=True,
    # )
    profile_picture = CompressedImageField(blank=True, null=True, width=1200)
    gender = models.CharField(
        choices=GENDER,
        max_length=10,
        blank=True,
        null=True,
    )
    date_of_birth = models.DateField(
        verbose_name="Date of Birth", blank=True, null=True
    )
    address = models.TextField(
        verbose_name="Address",
        blank=True,
        null=True,
    )
    phone_number = models.CharField(
        max_length=50, verbose_name="Phone Number", unique=True, blank=True, null=True
    )

    is_phone_verified = models.BooleanField(
        verbose_name="Is Phone Verified",
        default=False,
    )

    def __str__(self):
        return f"{self.full_name} - {self.user.email}"
