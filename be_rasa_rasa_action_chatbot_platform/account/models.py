from uuid import uuid4
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class AccountRole(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    role = models.CharField(max_length=50)
    description = models.TextField(max_length=200, null=True)

    def __str__(self):
        return f"{self.role}"


class Account(AbstractBaseUser, PermissionsMixin):
    GENDER = [
        ("male", "Male"),
        ("female", "Female")
    ]
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user_name = models.CharField(max_length=50, unique=True)
    email = models.EmailField(_("email address"), blank=True, default="", unique=True)
    full_name = models.CharField(max_length=100, blank=True, default="")
    employee_id = models.CharField(max_length=15, blank=True, default="")
    phone_number = models.CharField(max_length=15, blank=True, default="")
    image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')

    gender = models.CharField(max_length=10, choices=GENDER, blank=True, default="")
    role = models.ForeignKey(AccountRole, on_delete=models.SET_NULL, null=True)

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    last_login = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = "user_name"
    EMAIL_FIELD = "email"
    # The REQUIRED_FIELDS (except USERNAME_FIELD) is only applicable when using the "createsuperuser" management command
    REQUIRED_FIELDS = ["email"]

    objects = CustomUserManager()

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name or self.email.split("@")[0]

    def __str__(self):
        return self.user_name
