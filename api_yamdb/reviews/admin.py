from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Category, Genre, Title


@admin.register(User)
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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'category')
    search_fields = ('name',)
    list_filter = ('genre', 'category')
