from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Account


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = Account
        fields = ("user_name", "email", "image", "role",
                  "phone_number", "employee_id", "full_name", "gender")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = Account
        fields = ("user_name", "email", "image", "role",
                  "phone_number", "employee_id", "full_name", "gender")
