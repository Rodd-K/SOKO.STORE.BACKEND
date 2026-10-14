from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from catalog.models import Product
from .models import Order, OrderItem, DELIVERY_FEE


class OrderItemInputSerializer(serializers.Serializer):
    """What the frontend's cart sends in — just product + quantity.
    Price is deliberately NOT accepted from the client; it's looked up
    server-side so a tampered request can't under-charge an order."""

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    # write-only input list the frontend's checkout actually posts
    cart_items = OrderItemInputSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "status", "payment_method", "payment_status", "total",
            "full_name", "phone", "county", "town", "address",
            "created_at", "items", "cart_items",
        ]
        read_only_fields = ["id", "status", "payment_status", "total", "created_at"]

    def validate_cart_items(self, cart_items):
        if not cart_items:
            raise serializers.ValidationError("Cart is empty.")
        return cart_items

    def create(self, validated_data):
        cart_items = validated_data.pop("cart_items")
        user = self.context["request"].user

        # Everything below runs as one atomic transaction: either the whole
        # order is created and stock is decremented, or none of it is —
        # two customers can't both buy the last unit of something.
        with transaction.atomic():
            subtotal = Decimal("0")
            locked_products = {}

            for entry in cart_items:
                product = Product.objects.select_for_update().get(pk=entry["product_id"])
                if entry["quantity"] > product.stock:
                    raise serializers.ValidationError(
                        {"cart_items": f"Only {product.stock} of '{product.name}' left in stock."}
                    )
                locked_products[product.id] = product
                subtotal += product.selling_price * entry["quantity"]

            order = Order.objects.create(
                user=user,
                total=subtotal + DELIVERY_FEE,
                **validated_data,
            )

            for entry in cart_items:
                product = locked_products[entry["product_id"]]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=entry["quantity"],
                    price=product.selling_price,  # snapshot — future price changes won't alter this order
                )
                product.stock -= entry["quantity"]
                product.save(update_fields=["stock"])

            return order
