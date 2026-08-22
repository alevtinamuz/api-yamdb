from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .constants import (
    ROLE_MAX_LENGTH, EMAIL_MAX_LENGTH,
    NAME_MAX_LENGTH, SLUG_MAX_LENGTH
    ROLE_MAX_LENGTH, USERNAME_MAX_LENGTH, EMAIL_MAX_LENGTH,
    NAME_MAX_LENGTH, SLUG_MAX_LENGTH, MIN_SCORE, MAX_SCORE,
    REVIEW_MAX_LENGTH, COMMENT_MAX_LENGTH
)


class User(AbstractUser):
    class RoleChoices(models.TextChoices):
        USER = 'user', 'Пользователь'
        ADMIN = 'admin', 'Администратор'
        MODERATOR = 'moderator', 'Модератор'

    role = models.CharField(
        'Роль', max_length=ROLE_MAX_LENGTH,
        choices=RoleChoices.choices,
        default=RoleChoices.USER
    )
    bio = models.TextField(
        'Биография', blank=True
    )
    email = models.EmailField(
        'Email', max_length=EMAIL_MAX_LENGTH,
        unique=True
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return (
            self.role == self.RoleChoices.ADMIN
            or self.is_superuser
            or self.is_staff
        )

    @property
    def is_moderator(self):
        return self.role == self.RoleChoices.MODERATOR


class Genre(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH, verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=SLUG_MAX_LENGTH,
        verbose_name='Слаг',
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH, verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=SLUG_MAX_LENGTH,
        verbose_name='Слаг',
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH, verbose_name='Название'
    )
    year = models.PositiveSmallIntegerField(
        validators=[
            MaxValueValidator(
                limit_value=timezone.now().year,
                message='Год выпуска должен быть не больше текущего.'
            )
        ],
        verbose_name='Год выпуска'
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    text = models.TextField(
        'Текст отзыва',
        max_length=REVIEW_MAX_LENGTH
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[MinValueValidator(MIN_SCORE), MaxValueValidator(MAX_SCORE)]
    )
    pub_date = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        unique_together = ('title', 'author')
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'Отзыв {self.author} к {self.title}, оценка {self.score}'


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    text = models.TextField(
        'Текст комментария',
        max_length=COMMENT_MAX_LENGTH
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'Комментарий к отзыву'
        verbose_name_plural = 'Комментарии к отзывам'

    def __str__(self):
        return f'Комментарий {self.author} к {self.review}'
