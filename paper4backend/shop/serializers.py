from rest_framework.serializers import ModelSerializer, CharField
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404, get_list_or_404
from .models import (
    Products,
    ProductImage,
    Tags,
    Orders,
    ProductToOrder,
    OrderStatusChoices,
)
from paper4auth.models import Profile


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

    class Meta:
        fields = ["count", "product", "order"]
        model = ProductToOrder
        validators = []

    def create(self, validated_data: dict) -> ProductToOrder:
        product_id = validated_data["product"]
        order_id = validated_data["order"]
        count = validated_data["count"]
        existing = ProductToOrder.objects.filter(product=product_id, order=order_id).first()
        if existing:
            existing.count = count
            existing.save(update_fields=["count"])
            return existing
        return ProductToOrder.objects.create(**validated_data)


class OrderSerializer(ModelSerializer):
    products = ProductToOrderSerializer(many=True, read_only=True)
    chat_id = CharField(write_only=True)

    class Meta:
        fields = [
            "uuid",
            "status",
            "sender_service",
            "created_timestamp",
            "products",
            "chat_id",
        ]
        model = Orders

    def validate_chat_id(self, value: str | int) -> str | int:
        if not Profile.objects.filter(chat_id=value).exists():
            raise ValidationError(detail="Invalid chat_id.")
        return value

    def get_created_orders_by_profile(self, profile: Profile) -> Orders | None:
        return Orders.objects.filter(
            user__profiling=profile, status=OrderStatusChoices.CREATED
        ).first()

    def create(self, validated_data: dict) -> Orders:
        chat_id: str | int = validated_data.pop("chat_id")
        profile: Profile = get_object_or_404(Profile, chat_id=chat_id)
        if self.get_created_orders_by_profile(profile=profile):
            raise ValidationError(detail="Please pay for the last order.")

        order: Orders = Orders.objects.create(
            user=profile.user, status=OrderStatusChoices.CREATED
        )
        return order
