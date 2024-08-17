from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager for authentication.
    """

    def create_user(self, user_name, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not user_name:
            # the _ is the method to translate the response!
            raise ValueError(_("The Username must be set"))

        email = self.normalize_email(email)
        user = self.model(user_name=user_name, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, user_name, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(user_name, email, password, **extra_fields)
