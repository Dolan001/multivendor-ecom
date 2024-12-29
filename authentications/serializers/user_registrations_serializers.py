import random

from django.conf import settings
from django.contrib.auth.password_validation import (
    validate_password as validate_input_password,
)
from rest_framework import serializers, validators

from authentications.models import ROLE, User, UserInformation
# from promotions.utils import PointTransactions


class RegistrationSerializer(serializers.ModelSerializer):
    """
    New User Registration Serializer
    """

    retype_password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
        label="Retype Password",
    )

    full_name = serializers.CharField(
        required=True, write_only=True, source="user_information.full_name"
    )
    # is_verified = serializers.BooleanField(required=True, write_only=True)
    # phone_number = serializers.CharField(
    #     required=True, write_only=True, source="user_information.phone_number"
    # )
    # date_of_birth = serializers.CharField(
    #     required=True, write_only=True, source="user_information.date_of_birth"
    # )
    role = serializers.ChoiceField(
        choices=ROLE,
        # required=True,
        write_only=True,
        default="user",
    )

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "retype_password",
            "full_name",
            # "is_verified",
            # "phone_number",
            # "date_of_birth",
            "role",
        ]

    def validate_password(self, value):
        attrs = self.get_initial()

        if attrs.get("password") != attrs.get("retype_password"):
            raise serializers.ValidationError("Password fields didn't match.")

        # You can add additional password validation here
        validate_input_password(
            password=attrs.get("password"),
            user=User(email=attrs.get("email")),
        )

        return value

    # def validate_is_verified(self, value):
    #     attrs = self.get_initial()
    #     if not attrs.get("is_verified"):
    #         raise serializers.ValidationError("Email is not verified")
    #     return value

    def create(self, validated_data):
        information_user = validated_data.pop("user_information")
        validated_data.pop("retype_password")
        # is_verified = validated_data.pop("is_verified")
        user = User.objects.create_user(**validated_data, oauth_provider="email")
        user_info = user.user_information
        user_info.full_name = information_user["full_name"]
        # user_info.phone_number = information_user["phone_number"]
        # user_info.date_of_birth = information_user["date_of_birth"]

        user_info.save()

        # add points to user
        # PointTransactions().add_new_points(
        #     user=user, reason="SIGNUP", reference="Join the membership"
        # )

        return user


class VerifyIdentitySerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    secret = serializers.CharField(max_length=200, required=True)
    otp = serializers.CharField(max_length=100, required=True)
