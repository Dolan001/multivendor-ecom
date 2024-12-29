from django.db.models import Prefetch, Q
from rest_framework import viewsets, permissions
from rest_framework.response import Response

from product.models import Vendor
from product.serializers import VendorSerializer
from utils.extensions.permissions import IsAdminVendorOrReadOnly


class VendorViewSet(viewsets.ModelViewSet):
    serializer_class = VendorSerializer
    filterset_fields = ()
    ordering_fields = ("created_at", )
    search_fields = ["vendor_id", "name"]
    permission_classes = [permissions.IsAuthenticated, IsAdminVendorOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'vendor':
            queryset = Vendor.objects.filter(user=user, is_approved=True)
        elif user.role == 'customer':
            queryset = Vendor.objects.filter(is_approved=True)
        else:
            queryset = Vendor.objects.all()
        return queryset
