from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Email verification', {'fields': ('is_email_verified',)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
