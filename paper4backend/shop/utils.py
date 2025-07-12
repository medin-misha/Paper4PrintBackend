from django.shortcuts import get_object_or_404
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from .models import Products, Orders, OrderStatusChoices
from paper4auth.models import Profile


def get_order_by_chat_id(chat_id: str) -> Orders:
    return get_object_or_404(Orders, user__profiling__chat_id=chat_id, status=OrderStatusChoices.CREATED)

def modify_data_for_product_to_order_serializer(request: Request) -> dict:
    chat_id: str = request.data.get("chat_id")
    product_id: str = request.data.get("product_id")
    count: int = request.data.get("count")
    if not chat_id or not product_id or not count:
     raise ValidationError("fields: chat_id, product_id, count is valid")
    order = get_order_by_chat_id(chat_id=chat_id)
    product = get_object_or_404(Products, uuid=product_id)

    return {
        "order": order.uuid,
        "product": product.uuid,
        "count": count
    }
