from django.db.models import Sum
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from order.models import Order
from product.models import Vendor, Product


class AnalyticsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        vendors = Vendor.objects.all().count()
        products = Product.objects.all().count()
        orders = Order.objects.all()

        completed_orders = orders.filter(status="PURCHASE_CONFIRMATION")

        # Sum the `grand_total` field of these orders
        revenue = completed_orders.aggregate(total_revenue=Sum('grand_total'))['total_revenue']

        data = {
            'total_vendors': vendors,
            'total_products': products,
            'total_orders': orders.count(),
            'total_revenue': revenue or 0.0
        }

        return Response({'data': data}, status=status.HTTP_200_OK)