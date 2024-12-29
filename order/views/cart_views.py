from django.db.models import Prefetch
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from order.models import Cart, CartProduct
from order.serializers import (
    CartSerializer,
    CartProductSerializer,
)


class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.user)

    def clear_cart(self, request):
        cart_product = Cart.objects.filter(customer=request.user)
        cart_product.delete()
        return Response(
            {"message": "Cart cleared successfully"}, status=status.HTTP_200_OK
        )


class CartItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartProductSerializer

    def get_queryset(self):
        return CartProduct.objects.filter(cart__customer=self.request.user)


