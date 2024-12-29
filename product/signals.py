from django.db.models.signals import post_save
from django.dispatch import receiver
from product.models import *
from utils.helper.helper_functions import unique_slugify


@receiver(post_save, sender=Category)
@receiver(post_save, sender=SubCategory)
def create_instance_slug(sender, instance, created, **kwargs):
    if created:
        if isinstance(instance, Category):
            instance.slug = unique_slugify(instance, instance.title)
        if isinstance(instance, SubCategory):
            instance.slug = unique_slugify(instance, instance.title)
        instance.save()
