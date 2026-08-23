from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Avg

from .models import User, Category, Genre, Title, Review, Comment


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
    list_display = ('name', 'year', 'category', 'get_rating')
    search_fields = ('name',)
    list_filter = ('genre', 'category')

    @admin.display(description='Рейтинг')
    def get_rating(self, obj):
        """Возвращает средний рейтинг произведения."""
        rating = obj.reviews.aggregate(avg=Avg('score'))['avg']
        return round(rating, 2) if rating is not None else 0.0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'score',
                    'pub_date', 'short_text')
    search_fields = ('author__username', 'title__name', 'text')
    list_filter = ('score','pub_date')
    list_select_related = ('title', 'author')
    readonly_fields = ('pub_date',)

    @admin.display(description='Текст')
    def short_text(self, obj):
        """Возвращает сокращённый текст отзыва."""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'author',
                    'pub_date', 'short_text')
    search_fields = ('author__username', 'review__text', 'text')
    list_filter = ('pub_date',)
    list_select_related = ('review', 'author')
    readonly_fields = ('pub_date',)

    @admin.display(description='Текст')
    def short_text(self, obj):
        """Возвращает сокращённый текст комментария."""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
