from django.db.models import Prefetch, Q
from rest_framework import viewsets, permissions
from rest_framework.response import Response

from product.models import Product
from product.serializers import ProductSerializer, ProductListSerializer
from utils.extensions.permissions import IsAdminVendorOrReadOnly


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    lookup_field = "slug"
    filterset_fields = (
        "vendor__vendor_id",
        "category__slug",
        "subcategory__slug",
        "stock"
    )
    ordering_fields = ("created_at", "rating", "total_likes", "total_sold", "price")
    search_fields = ["category__title", "subcategory__title", "name"]
    permission_classes = [permissions.IsAuthenticated, IsAdminVendorOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        price_min = self.request.query_params.get("price_min")
        price_max = self.request.query_params.get("price_max")

        if user.role == 'vendor':
            queryset = Product.objects.filter(vendor__user=user).order_by("-created_at")
        else:
            if price_min and price_max:
                queryset = Product.objects.filter(
                    price__gte=price_min,
                    price__lte=price_max,
                ).order_by("-created_at")
            else:
                queryset = Product.objects.all().order_by("-created_at")
        return queryset

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ProductListSerializer
        else:
            return ProductSerializer
