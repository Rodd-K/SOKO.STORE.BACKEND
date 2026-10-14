from rest_framework import generics, permissions
from .models import Order
from .permissions import IsAdminRole
from .serializers import OrderSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    """
    GET /api/orders/  -> the logged-in user's own orders
    POST /api/orders/ -> place a new order from the cart
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items").order_by("-created_at")

    def perform_create(self, serializer):
        # user is pulled from context["request"].user inside OrderSerializer.create()
        # itself — don't also pass it here, or it collides as a duplicate kwarg.
        serializer.save()


class OrderDetailView(generics.RetrieveAPIView):
    """GET /api/orders/:id/ — only the owning user can view it."""

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


class AdminOrderListView(generics.ListAPIView):
    """GET /api/admin/orders/?status=processing — every order, for the admin dashboard."""

    serializer_class = OrderSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        qs = Order.objects.all().prefetch_related("items").order_by("-created_at")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs
