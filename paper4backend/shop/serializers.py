from rest_framework.serializers import ModelSerializer
from .models import Products, ProductImage, Tags

class ProductImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [
            "file"
        ]

class TagSerializer(ModelSerializer):
    class Meta:
        model = Tags
        fields =["name", "slag"]


class ProductSerializer(ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    class Meta:
        fields = [
            "name", "description", "price", "sale", "created_at", "updated_at", "is_archive", "images", "tags"
        ]
        model = Products

# uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(null=False, blank=False)
#     description = models.TextField(null=True, blank=True)
#     price = models.DecimalField(
#         null=False, max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
#     )
#     sale = models.IntegerField(
#         default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
#     )
#     is_archive = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)