from django.db.models.signals import post_save
from django.dispatch import receiver

from order.models import OrderProduct, Order


# @receiver(post_save, sender=Order)
# def update_total_sold(sender, instance, **kwargs):
#     print(instance.orders.all())
#     if instance.status == "PAYMENT_COMPLETE":
#         product = instance.orders.all()
#         print(product)
#         # product.total_sold += 1
#         # product.save()
#     if instance.status == "CANCEL_COMPLETE":
#         product = instance.orders.all()
#         print(product)
#         # if product.total_sold > 0:
#         #     product.total_sold -= 1
#         #     product.save()
