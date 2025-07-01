from django.db import models
from django.contrib.auth.models import User
import uuid


class Profile(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    phone = models.CharField(null=True, blank=True)
    chat_id = models.CharField(null=False, blank=False)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name="profiling")