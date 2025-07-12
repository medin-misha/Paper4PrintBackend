from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .filters import ProductTagsFilter
from .serializers import ProductSerializer, OrderSerializer, ProductToOrderSerializer
from .models import Products, Orders, OrderStatusChoices, ProductToOrder
from .utils import modify_data_for_product_to_order_serializer, get_order_by_chat_id


class ProductsReadOnlyViewSet(ReadOnlyModelViewSet):
    queryset = Products.objects.prefetch_related("images").all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["name", "price", "sale", "created_at", "updated_at", "tags"]
    ordering = ["name"]
    filterset_class = ProductTagsFilter


class OrdersViewSet(ViewSet):
    def retrieve(self, request: Request) -> Response:
        chat_id: str = request.GET.get("chat_id")
        if not chat_id:
            raise ValidationError("Please add query params chat_id.")

        order = get_object_or_404(
            Orders, user__profiling__chat_id=chat_id, status=OrderStatusChoices.CREATED
        )

        serializer = OrderSerializer(order)
        return Response({"order": serializer.data})

    def create(self, request: Request) -> Response:
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"order": serializer.data})

    def update(self, request: Request) -> Response:
        """Добавление продукта"""
        serializer = ProductToOrderSerializer(data=modify_data_for_product_to_order_serializer(request=request))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"product_to_order": serializer.data})

    def destroy(self, request: Request) -> Response:
        chat_id: str = request.query_params.get("chat_id")
        product_id: str = request.query_params.get("product_id")
        order = get_order_by_chat_id(chat_id=chat_id)
        product = get_object_or_404(Products, uuid=product_id)
        product_to_order = get_object_or_404(ProductToOrder, order=order, product=product)
        product_to_order.delete()
        product_to_order.save()
        return Response(status=204)

