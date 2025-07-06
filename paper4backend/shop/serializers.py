from rest_framework.serializers import ModelSerializer
from .models import Products, ProductImage, Tags, Orders, ProductToOrder


class ProductImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["file"]


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tags
        fields = ["name", "slag"]


class ProductSerializer(ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        fields = [
            "name",
            "description",
            "price",
            "sale",
            "created_at",
            "updated_at",
            "is_archive",
            "images",
            "tags",
        ]
        model = Products


class ProductToOrderSerializer(ModelSerializer):
    product = ProductSerializer(many=False, read_only=True)

    class Meta:
        fields = ["count", "product"]
        model = ProductToOrder


class OrderSerializer(ModelSerializer):
    products = ProductToOrderSerializer(many=True, read_only=True)

    class Meta:
        fields = [
            "uuid",
            "status",
            "sender_service",
            "created_timestamp",
            "products",
        ]
        model = Orders
