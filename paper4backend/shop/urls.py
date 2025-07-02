from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("products/", views.ProductsReadOnlyViewSet.as_view({"get": "list"}), name="products_list"),
]
