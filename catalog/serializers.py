from rest_framework import serializers
from .models import Category, Product, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.first_name", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "product", "user", "user_name", "rating", "comment", "created_at"]
        read_only_fields = ["user"]


class ProductSerializer(serializers.ModelSerializer):
    """Used for both list and detail — the frontend's mock product shape
    already matches these field names, so swapping fetch() in is a 1:1 map."""

    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    rating = serializers.FloatField(source="average_rating", read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    selling_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "description", "price", "discount_price", "selling_price",
            "stock", "in_stock", "image", "category", "category_id",
            "rating", "created_at",
        ]

    def validate(self, data):
        price = data.get("price", getattr(self.instance, "price", None))
        discount = data.get("discount_price", getattr(self.instance, "discount_price", None))
        if discount is not None and price is not None and discount >= price:
            raise serializers.ValidationError(
                {"discount_price": "Discount price must be lower than the normal price."}
            )
        return data
