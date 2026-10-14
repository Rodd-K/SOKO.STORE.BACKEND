from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total", "status", "payment_method", "created_at")
    list_filter = ("status", "payment_method")
    list_editable = ("status",)  # change Pending -> Confirmed -> ... right from the list
    inlines = [OrderItemInline]
