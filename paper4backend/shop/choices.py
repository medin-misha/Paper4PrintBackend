from django.db import models


class OrderStatusChoices(models.TextChoices):
    CREATED = "CREATED", "Created"
    PAID = "PAID", "Paid"
    PROCESSED = "PROCESSED", "Processed"
    SUCCESS = "SUCCESS", "Success"
    CANCELLED = "CANCELLED", "Cancelled"
    FAILED = "FAILED", "Failed"
    RETURNED = "RETURNED", "Returned"


class PaidStatusChoices(models.TextChoices):
    CREATED = "CREATED", "Created"
    PAID = "PAID", "Paid"
    FAILED = "FAILED", "Failed"


class CurrencyChoices(models.TextChoices):
    EUR = "EUR", "Евро"
    USD = "USD", "Доллар"
    RUB = "RUB", "Рубль"
    UAH = "UAH", "Гривна"
