from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Orders, Payment


@receiver(post_save, sender=Orders)
def create_payment_for_orders(
    sender: Orders, instance: Orders, created: bool, **kwargs
):
    """
    Создание Payment к Orders
    """
    if created:
        Payment.objects.create(order=instance)
