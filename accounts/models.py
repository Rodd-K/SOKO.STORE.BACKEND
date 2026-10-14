from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Extends Django's built-in User so we get password hashing, login,
    and admin support for free — just adding the fields Soko needs on
    top (phone, role). email is used as the login field instead of
    username, matching the frontend's login form.
    """

    ROLE_CHOICES = [
        ("customer", "Customer"),
        ("admin", "Admin"),
    ]

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="customer")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        # A Django superuser (created with `createsuperuser`) is always a Soko admin,
        # otherwise the API's admin-only endpoints would reject them.
        if self.is_superuser:
            self.role = "admin"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
