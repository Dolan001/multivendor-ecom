import uuid

from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class Cart(BaseModel):
    customer = models.ForeignKey(
        "authentications.User", related_name="customer_cart", on_delete=models.CASCADE
    )
    product_amount = models.FloatField(default=0.0, null=True, blank=True)
    discount = models.FloatField(default=0.0, null=True, blank=True)
    grand_total = models.FloatField(default=0.0, null=True, blank=True)
    delivery_charge = models.FloatField(default=0.0, null=True, blank=True)

    class Meta:
        ordering = [
            "-updated_at",
        ]

    def __str__(self):
        return str(self.customer)


class CartProduct(BaseModel):
    cart = models.ForeignKey(
        Cart, related_name="carts", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        "product.Product",
        related_name="cart_products",
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return str(self.cart)
