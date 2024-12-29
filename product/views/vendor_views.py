from django.db.models import Prefetch, Q, Sum
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from order.models import Order
from product.models import Vendor, Product
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

    def vendor_analytics(self, request, *args, **kwargs):
        user = request.user
        if user.role == 'vendor':
            products = Product.objects.all().count()
            orders = Order.objects.filter(vendor__user=request.user)

            completed_orders = orders.filter(status="PURCHASE_CONFIRMATION")

            # Sum the `grand_total` field of these orders
            revenue = completed_orders.aggregate(total_revenue=Sum('grand_total'))['total_revenue']

            data = {
                'total_products': products,
                'total_orders': orders.count(),
                'total_revenue': revenue or 0.0
            }

            return Response({'data': data}, status=status.HTTP_200_OK)
        return Response({'detail': 'You do not have permission'}, status=status.HTTP_403_FORBIDDEN)
