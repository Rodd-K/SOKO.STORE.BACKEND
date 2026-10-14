from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, MeView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    # Login: POST {"email": "...", "password": "..."} -> {"access": ..., "refresh": ...}
    # (User.USERNAME_FIELD = "email", so simplejwt's default view already expects email here.)
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="me"),
]
