import pyotp
from django.db.models.signals import post_save
from django.dispatch import receiver

from authentications.models import User, UserInformation


@receiver(post_save, sender=User)
def create_user_instance(sender, instance, created, **kwargs):
    if created:
        UserInformation.objects.create(
            user=instance,
        )
