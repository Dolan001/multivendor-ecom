from rest_framework import serializers

from authentications.models import User, UserInformation
# from order.models import OrderAddress


class UserInformationSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(source="user.is_active", required=False)
    # phone_number = serializers.CharField(source="user.phone_number", required=False)

    class Meta:
        model = UserInformation
        fields = (
            "id",
            "full_name",
            "profile_picture",
            "gender",
            "address",
            "phone_number",
            "date_of_birth",
            "is_active",
        )

    def update(self, instance, validated_data):
        user = self.instance.user
        user_info = validated_data.get("user")
        if user_info:
            user.is_active = user_info.get("is_active", instance.user.is_active)
            user.save()
        instance.full_name = validated_data.get("full_name", instance.full_name)
        instance.profile_picture = validated_data.get(
            "profile_picture", instance.profile_picture
        )
        instance.gender = validated_data.get("gender", instance.gender)
        instance.date_of_birth = validated_data.get(
            "date_of_birth", instance.date_of_birth
        )
        instance.address = validated_data.get("address", instance.address)
        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    user_information = UserInformationSerializer(read_only=True)
    is_address = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "date_joined",
            "is_verified",
            "is_address",
            "is_active",
            "user_information",
        )

    # def get_is_address(self, obj):
    #     request = self.context.get("request")
    #     order_address = OrderAddress.objects.filter(user=request.user)
    #     if order_address:
    #         data = True
    #     else:
    #         data = False
    #     return data
