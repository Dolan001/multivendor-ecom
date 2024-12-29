from rest_framework import permissions


class IsAuthenticatedAndEmailVerified(permissions.BasePermission):
    """
    Allows access only to authenticated users who are verified.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_verified
        )


class IsAuthenticatedAndEmailNotVerified(permissions.BasePermission):
    """
    Allows access only to authenticated users without a verified email.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and not request.user.is_verified
        )


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_superuser)


class IsAdminVendorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user.role == 'admin' or request.user.role == 'vendor')

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # if obj.is_private:
            #     email_list = [email[0] for email in list(obj.joined_gathering.all().values_list('member__email'))]
            #     return request.user.email in email_list
            return True

        user = request.user

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            # print('patch', is_moderator)
            return bool(user.role == 'admin' or user.role == 'vendor')
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsUserOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user
