from django.contrib import admin
from .models import ProductImage, Orders, Products, ProductToOrder


class ProductToOrderInline(admin.TabularInline):
    extra = 1
    model = ProductToOrder


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    pass


@admin.register(Orders)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ["status", "user", "created_timestamp"]
    inlines = [ProductToOrderInline]


@admin.register(Products)
class ProductsModelAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    inlines = [ProductToOrderInline]


@admin.register(ProductToOrder)
class ProductToOrder(admin.ModelAdmin):
    pass
