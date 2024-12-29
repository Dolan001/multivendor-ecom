from django.db.models import Prefetch
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from order.models import OrderProduct, Order
from order.serializers import (
    OrderSerializer,
    OrderProductSerializer,
)


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'vendor':
            queryset = Order.objects.filter(vendor__user=self.request.user)
        elif user.role == 'admin':
            queryset = Order.objects.all()
        else:
            queryset = Order.objects.filter(customer=self.request.user)
        return queryset


class OrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderProductSerializer

    def get_queryset(self):
        return OrderProduct.objects.filter(order__customer=self.request.user)


