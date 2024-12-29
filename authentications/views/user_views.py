from rest_framework import permissions, response, status, viewsets
from rest_framework.response import Response

from authentications.models import User, UserInformation
from authentications.serializers import UserInformationSerializer, UserSerializer


class UserViews(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete"]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.action == "logout":
            return []
        return self.serializer_class

    def profile(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "You are not authenticated"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = self.get_serializer(user)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user_id = kwargs.pop("id", None)
        user = self.request.user
        instance = self.get_object()

        if user.id == user_id:
            instance.delete()
        return Response(
            {"detail": "Can not permanently delete others account"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserInformationUpdateView(viewsets.ModelViewSet):
    serializer_class = UserInformationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch"]

    def get_object(self):
        return UserInformation.objects.get(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=kwargs.get("partial", False)
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        user_id = instance.user
        user_serializer = UserSerializer(user_id, context={"request": request})
        return Response(
            {"data": user_serializer.data, "message": "Profile updated successfully"},
            status=status.HTTP_200_OK,
        )
