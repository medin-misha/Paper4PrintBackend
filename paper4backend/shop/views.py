from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import ProductSerializer
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductTagsFilter
from .models import Products

class ProductsReadOnlyViewSet(ReadOnlyModelViewSet):
    queryset = Products.objects.prefetch_related("images").all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["name", "price", "sale", "created_at", "updated_at", "tags"]
    ordering = ["name"]
    filterset_class = ProductTagsFilter
