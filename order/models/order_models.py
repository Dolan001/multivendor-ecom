import uuid

from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel
from product.models import Vendor

STATUS = [
    ("PENDING", _("Pending")),
    ("PAYMENT_COMPLETE", _("Payment Complete")),
    ("PRODUCT_IN_PRODUCTION", _("Product in Production")),
    ("IN_DELIVERY", _("In Delivery")),
    ("DELIVERY_COMPLETE", _("Delivery Complete")),
    ("PURCHASE_CONFIRMATION", _("Purchase Confirmation")),
    ("RETURN_REQUEST", _("Return Request")),
    ("RETURNED_IN_PROGRESS", _("Returned in Progress")),
    ("RETURN_COMPLETE", _("Return Complete")),
    ("CANCEL_REQUEST", _("Cancel Request")),
    ("CANCEL_IN_PROGRESS", _("Cancel in Progress")),
    ("CANCEL_COMPLETE", _("Cancel Complete")),
]

class Order(BaseModel):
    """
    # ==================================
    # order of products
    # ==================================
    """

    PAYMENT_TYPE = (
        ("NONE", "None"),
        ("CASH_ON_DELIVERY", "Cash on delivery"),
        ("ONLINE_PAYMENT", "Online payment"),
        ("PARTIAL_PAYMENT", "Partial payment"),
    )
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_orders', null=True)
    order_id = models.CharField(
        max_length=255, unique=True, editable=False, db_index=True
    )
    delivery_number = models.CharField(max_length=100, null=True, blank=True)
    customer = models.ForeignKey(
        "authentications.User", related_name="customer_orders", on_delete=models.CASCADE
    )
    product_amount = models.FloatField(default=0.0, null=True, blank=True)
    discount = models.FloatField(default=0.0, null=True, blank=True)
    grand_total = models.FloatField(default=0.0, null=True, blank=True)
    delivery_charge = models.FloatField(default=0.0, null=True, blank=True)
    shipping_address = models.TextField()
    status = models.CharField(choices=STATUS, default="PENDING", max_length=50)
    payment = models.CharField(
        max_length=50,
        choices=PAYMENT_TYPE,
        default="NONE",
    )
    payment_key = models.CharField(max_length=255, blank=True, null=True)
    payment_type = models.CharField(max_length=20, blank=True, null=True)
    payment_response = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = [
            "-updated_at",
        ]

    def save(self, *args, **kwargs):
        if not self.order_id:
            with transaction.atomic():
                # First save to get the pk
                self.order_id = f"TEMP-{uuid.uuid4()}"
                super().save(*args, **kwargs)
                # Now generate the order_id
                # "ORD{YEAR}{MONTH}{DAY}{000000PK}"
                self.order_id = f"ORD{self.created_at.strftime('%Y%m%d')}{self.pk:06d}"
                # Save again to store the generated order_id
                super().save(update_fields=["order_id"])
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return str(self.order_id)


# ============**********============
# product order models
# ============**********============


class OrderProduct(BaseModel):
    order = models.ForeignKey(
        Order, related_name="orders", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        "product.Product",
        related_name="product_orders",
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return str(self.order)
