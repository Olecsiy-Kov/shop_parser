from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "manufacturer", "price_regular", "reviews_count")
    search_fields = ("name", "product_code", "manufacturer")
