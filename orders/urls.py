from django.urls import path
from .views import OrderListCreateView, OrderDetailView, AdminOrderListView

urlpatterns = [
    path("orders/", OrderListCreateView.as_view(), name="order-list"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("admin/orders/", AdminOrderListView.as_view(), name="admin-order-list"),
]
