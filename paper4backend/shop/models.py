from tkinter.constants import CASCADE

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
import uuid


class OrderStatusChoices(models.TextChoices):
    CREATED = "CREATED", "Created"
    PAID = "PAID", "Paid"
    PROCESSED = "PROCESSED", "Processed"
    SUCCESS = "SUCCESS", "Success"
    CANCELLED = "CANCELLED", "Cancelled"
    FAILED = "FAILED", "Failed"
    RETURNED = "RETURNED", "Returned"


# Create your models here.
class Orders(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(to=User, related_name="orders", on_delete=models.CASCADE)
    # CREATED, PAID, PROCESSED, SUCCESS, CANCELLED, FAILED
    status = models.CharField(
        null=False,
        default=OrderStatusChoices.CREATED,
        choices=OrderStatusChoices.choices,
    )
    sender_service = models.CharField(null=True)
    created_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Order {self.uuid} - {self.user.username} - {self.status}"


class Products(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(
        null=False, max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    sale = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_archive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProductImage(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to="product/images/", null=False)
    product = models.ForeignKey(
        to=Products, on_delete=models.CASCADE, null=True, related_name="images"
    )