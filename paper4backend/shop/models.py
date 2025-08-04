from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import slugify
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
    tags = models.ManyToManyField(to="Tags", related_name="products")


class ProductImage(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to="product/images/", null=False)
    product = models.ForeignKey(
        to=Products, on_delete=models.CASCADE, null=True, related_name="images"
    )


class ProductToOrder(models.Model):
    product = models.ForeignKey(
        to=Products, on_delete=models.CASCADE, null=False, related_name="orders"
    )
    order = models.ForeignKey(
        to=Orders, on_delete=models.CASCADE, null=False, related_name="products"
    )
    count = models.IntegerField(default=0, validators=[MinValueValidator(1)])

    # Уникальность пары product-order
    class Meta:
        unique_together = ("product", "order")

    def __str__(self) -> str:
        return f"{self.product.name} * {self.count} in {self.order.user.username}"


class Tags(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    slag = models.SlugField(unique=True, blank=True, max_length=100)

    def save(self, *args, **kwargs):
        if not self.slag:
            self.slag = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name}"

class PaidStatusChoices(models.TextChoices):
    CREATED = "CREATED", "Created"
    PAID = "PAID", "Paid"
    FAILED = "FAILED", "Failed"

class Payment(models.Model):
    uuid = models.UUIDField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        default=PaidStatusChoices.CREATED,
        choices=PaidStatusChoices
    )
    order = models.ForeignKey(to=Orders, on_delete=models.CASCADE, related_name="payment")

    def amount(self) -> float:
        for pto in self.order.products:
            print(pto)
