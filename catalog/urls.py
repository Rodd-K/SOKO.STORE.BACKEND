from django.urls import path
from .views import CategoryListView, ProductListCreateView, ProductDetailView, ReviewCreateView

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("products/", ProductListCreateView.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("products/<int:product_id>/reviews/", ReviewCreateView.as_view(), name="product-reviews"),
]
