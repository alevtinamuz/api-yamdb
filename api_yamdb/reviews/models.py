from django.core.validators import MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .constants import (
    ROLE_MAX_LENGTH, EMAIL_MAX_LENGTH,
    NAME_MAX_LENGTH, SLUG_MAX_LENGTH
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
