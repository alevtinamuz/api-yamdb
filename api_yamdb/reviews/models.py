from django.contrib.auth.models import AbstractUser
from django.db import models


ROLE_MAX_LENGTH = 20
USERNAME_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 254


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
    username = models.CharField(
        'Username пользователя',
        max_length=USERNAME_MAX_LENGTH,
        unique=True
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
        return self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role == 'moderator'
