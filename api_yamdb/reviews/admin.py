from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'role',
        'is_staff'
    )
    list_editable = (
        'role',
        'is_staff'
    )
    search_fields = (
        'username',
    )
    list_filter = (
        'role',
    )


admin.site.register(User, CustomUserAdmin)
