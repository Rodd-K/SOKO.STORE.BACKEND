from django.db.models import Q
from rest_framework import generics, permissions
from .models import Category, Product, Review
from .permissions import IsAdminOrReadOnly
from .serializers import CategorySerializer, ProductSerializer, ReviewSerializer


class CategoryListView(generics.ListCreateAPIView):
    """GET /api/categories/ — list. POST — admin only (category_id write handled on Product)."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductListCreateView(generics.ListCreateAPIView):
    """
    GET /api/products/?category=phones&q=iphone&sort=price-asc&maxPrice=20000
    Mirrors the exact query params the frontend's Products.jsx already sends.
    """

    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Product.objects.select_related("category").all()

        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category__slug=category)

        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

        max_price = self.request.query_params.get("maxPrice")
        if max_price:
            qs = qs.filter(price__lte=max_price)

        sort = self.request.query_params.get("sort", "newest")
        if sort == "price-asc":
            qs = qs.order_by("price")
        elif sort == "price-desc":
            qs = qs.order_by("-price")
        else:
            qs = qs.order_by("-id")

        return qs


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/DELETE /api/products/:id/"""

    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]


class ReviewCreateView(generics.ListCreateAPIView):
    """GET/POST /api/products/:id/reviews/"""

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_id"])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, product_id=self.kwargs["product_id"])
