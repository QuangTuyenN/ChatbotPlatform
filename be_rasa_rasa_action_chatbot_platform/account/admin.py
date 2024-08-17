from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Account
from .models import AccountRole


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = Account
    list_display = ("user_name", "full_name", "is_superuser", "is_staff", "is_active")
    list_filter = ("user_name", "full_name", "is_superuser", "is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("user_name", "email", "password", "image", "role",
                           "phone_number", "employee_id", "full_name", "gender")}),
        ("Permissions", {"fields": ("is_superuser", "is_staff", "is_active")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "user_name", "email", "password1", "password2",
                "phone_number", "employee_id", "full_name", "image", "role", "gender",
                "is_superuser", "is_staff", "is_active"
            )}
         ),
    )
    search_fields = ("full_name",)
    ordering = ("user_name",)


admin.site.register(AccountRole)
admin.site.register(Account, CustomUserAdmin)
