from django_filters import rest_framework as filters
from .models import Products


class ProductTagsFilter(filters.FilterSet):
    tags = filters.CharFilter(field_name="tags__name", lookup_expr="icontains")
    class Meta:
        model = Products
        fields = ["tags"]
