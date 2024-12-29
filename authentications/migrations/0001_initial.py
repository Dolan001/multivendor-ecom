# Generated by Django 5.0.3 on 2024-12-29 06:40

import core.models
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=100, unique=True, verbose_name="Email"
                    ),
                ),
                (
                    "oauth_provider",
                    models.CharField(
                        choices=[
                            ("google", "google"),
                            ("apple", "apple"),
                            ("kakao", "kakao"),
                            ("email", "email"),
                        ],
                        max_length=10,
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("admin", "Admin"),
                            ("vendor", "Vendor"),
                            ("customer", "Customer"),
                        ],
                        default="user",
                        max_length=10,
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(auto_now_add=True, verbose_name="Date Joined"),
                ),
                ("last_login", models.DateTimeField(auto_now=True)),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designate if the user has superuser status",
                        verbose_name="Superuser Status",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designate if the user has staff status",
                        verbose_name="Staff Status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designate if the user has active status",
                        verbose_name="Active Status",
                    ),
                ),
                (
                    "is_verified",
                    models.BooleanField(
                        default=False,
                        help_text="Email Verified",
                        verbose_name="Email Verified",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="UserInformation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "full_name",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="Full Name"
                    ),
                ),
                (
                    "profile_picture",
                    core.models.CompressedImageField(
                        blank=True,
                        null=True,
                        quality=85,
                        upload_to=core.models.CompressedImageField.get_content_file_path,
                        width=1200,
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("male", "male"),
                            ("female", "female"),
                            ("other", "other"),
                        ],
                        max_length=10,
                        null=True,
                    ),
                ),
                (
                    "date_of_birth",
                    models.DateField(
                        blank=True, null=True, verbose_name="Date of Birth"
                    ),
                ),
                (
                    "address",
                    models.TextField(blank=True, null=True, verbose_name="Address"),
                ),
                (
                    "phone_number",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        unique=True,
                        verbose_name="Phone Number",
                    ),
                ),
                (
                    "is_phone_verified",
                    models.BooleanField(
                        default=False, verbose_name="Is Phone Verified"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_information",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]