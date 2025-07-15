from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from typing import Dict, List

from .filters import ProductTagsFilter
from .serializers import (
    ProductSerializer,
    OrderSerializer,
    ProductToOrderSerializer,
    CreateOrderRequestSerializer,
    AddProductInOrderRequestSerializer,
)
from .models import Products, Orders, OrderStatusChoices, ProductToOrder
from .utils import modify_data_for_product_to_order_serializer, get_order_by_chat_id


@extend_schema(summary="Get products")
class ProductsReadOnlyViewSet(ReadOnlyModelViewSet):
    queryset = Products.objects.prefetch_related("images").all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["name", "price", "sale", "created_at", "updated_at", "tags"]
    ordering = ["name"]
    filterset_class = ProductTagsFilter


extend_schema(summary="Orders CRUD")


class OrdersViewSet(ViewSet):
    @extend_schema(
        summary="Get last created Order or return 404",
        responses={200: OrderSerializer, 404: Dict[str, str]},
        parameters=[
            OpenApiParameter(type=str, name="chat_id", location=OpenApiParameter.QUERY)
        ],
    )
    def retrieve(self, request: Request) -> Response:
        chat_id: str = request.GET.get("chat_id")
        if not chat_id:
            raise ValidationError("Please add query params chat_id.")

        order = get_object_or_404(
            Orders, user__profiling__chat_id=chat_id, status=OrderStatusChoices.CREATED
        )

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @extend_schema(
        summary="Create new Order if not CREATED Order",
        request=CreateOrderRequestSerializer,
        responses={200: OrderSerializer, 400: Dict[str, list] | List[str]},
    )
    def create(self, request: Request) -> Response:
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        summary="Add or update Product in current CREATED Order by chat_id",
        request=AddProductInOrderRequestSerializer,
        responses={200: ProductToOrderSerializer, 400: Dict[str, list] | List[str]},
    )
    def update(self, request: Request) -> Response:
        serializer = ProductToOrderSerializer(
            data=modify_data_for_product_to_order_serializer(request=request)
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        summary="Remove product from order",
        parameters=[
            OpenApiParameter(type=str, name="chat_id", location=OpenApiParameter.QUERY),
            OpenApiParameter(
                type=str, name="product_id", location=OpenApiParameter.QUERY
            ),
        ],
        responses={204: None, 404: Dict[str, str], 400: Dict[str, str]},
    )
    def destroy(self, request: Request) -> Response:
        chat_id: str = request.query_params.get("chat_id")
        product_id: str = request.query_params.get("product_id")
        order = get_order_by_chat_id(chat_id=chat_id)
        product = get_object_or_404(Products, uuid=product_id)
        product_to_order = get_object_or_404(
            ProductToOrder, order=order, product=product
        )
        product_to_order.delete()
        product_to_order.save()
        return Response(status=204)
