from django.urls import path
from rest_framework.routers import DefaultRouter

from order.views import (
    CartItemViewSet,
    CartViewSet,
    OrderViewSet,
    OrderItemViewSet
#    OrderAddressViewSet,
#     OrderItemsViewSet,
#     OrderProductViewSet,
#     PlaceOrderViewSet,
#     ShippingRequestViewSet,
)

router = DefaultRouter()

router.register(r"cart", CartViewSet, basename="cart")
router.register(r"cart-item", CartItemViewSet, basename="cart-item")
router.register(r"order", OrderViewSet, basename="order")
router.register(r"order-item", OrderItemViewSet, basename="order-item")

# router.register(r"order-address", OrderAddressViewSet, basename="order-address")
# router.register(r"place-order", PlaceOrderViewSet, basename="place-order")
# router.register(r"orders", OrderItemsViewSet, basename="order_item")
# router.register(r"order-product", OrderProductViewSet, basename="order_product")
# router.register(
#     r"shipping-request", ShippingRequestViewSet, basename="shipping_request"
# )

urlpatterns = [
    # path(
    #     "recent-orders/",
    #     OrderItemsViewSet.as_view({"get": "recent_orders"}),
    #     name="recent_orders",
    # ),
    # path(
    #     "make-payment/",
    #     PlaceOrderViewSet.as_view({"post": "make_payment"}),
    #     name="make_payment",
    # ),
    # path(
    #     "cancel-payment/",
    #     PlaceOrderViewSet.as_view({"post": "cancel_payment"}),
    #     name="cancel_payment",
    # ),
    # path(
    #     "default-address/",
    #     OrderAddressViewSet.as_view({"get": "default_address"}),
    #     name="default_address",
    # ),
    # path(
    #     "bulk-order-status-update/",
    #     PlaceOrderViewSet.as_view({"post": "bulk_order_status_update"}),
    # ),
    path("clear-cart/", CartViewSet.as_view({"delete": "clear_cart"})),
]
urlpatterns += router.urls
