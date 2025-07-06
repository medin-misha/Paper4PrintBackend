from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductTagsFilter
from .serializers import ProductSerializer, OrderSerializer
from .models import Products, Orders


class ProductsReadOnlyViewSet(ReadOnlyModelViewSet):
    queryset = Products.objects.prefetch_related("images").all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["name", "price", "sale", "created_at", "updated_at", "tags"]
    ordering = ["name"]
    filterset_class = ProductTagsFilter


class OrdersViewSet(ViewSet):
    def retrieve(self, request: Request) -> Response:
        order_id: str = request.GET.get("id")
        chat_id: str = request.GET.get("chat_id")
        if not order_id or not chat_id:
            raise NotFound(
                "Pleace add query params chat_id and id. chat_id is telegram chat_id and id is order id."
            )

        order = Orders.objects.get(uuid=order_id, user__profiling__chat_id=chat_id)
        print(order.uuid, order.products, order.created_timestamp)
        serializer = OrderSerializer(order)
        return Response({"order": serializer.data})
