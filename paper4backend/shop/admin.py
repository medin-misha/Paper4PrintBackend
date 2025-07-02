from django.contrib import admin
from .models import ProductImage, Orders, Products, ProductToOrder, Tags


class ProductToOrderInline(admin.TabularInline):
    extra = 1
    model = ProductToOrder

class ProductImageInline(admin.TabularInline):
    extra = 1
    model = ProductImage


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    pass


@admin.register(Orders)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ["status", "user", "created_timestamp"]
    inlines = [ProductToOrderInline]
    list_filter = ["status", "user"]
    ordering = ["-created_timestamp", "status"]


@admin.register(Products)
class ProductsModelAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [ProductImageInline,]
    filter_horizontal = ["tags",]
    search_fields = ["name", "price", "description"]


@admin.register(ProductToOrder)
class ProductToOrder(admin.ModelAdmin):
    search_fields = ["product", "order"]

@admin.register(Tags)
class TagsModelAdmin(admin.ModelAdmin):
    list_display = ["name", "slag"]
    search_fields = ["name", "slag"]
