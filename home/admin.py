from django.contrib import admin
from .models import Product, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'is_sale']
    list_filter = ['category', 'is_sale']
    search_fields = ['name', 'category']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'date', 'status']
    list_filter = ['status']
    search_fields = ['id', 'customer__name']
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity']
    list_filter = ['product']
    search_fields = ['order__id', 'product__name']


# Register your models here.
