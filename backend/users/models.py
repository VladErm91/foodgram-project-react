from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import (CASCADE, CharField, EmailField, ForeignKey,
                              Model, UniqueConstraint, CheckConstraint, F, Q)


class User(AbstractUser):
    """ Модель пользователя """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', )
    first_name = CharField(
        verbose_name='Имя',
        max_length=settings.LENGTH_FIELD_USER_1
    )
    last_name = CharField(
        max_length=settings.LENGTH_FIELD_USER_1,
        verbose_name='Фамилия',
    )
    email = EmailField(
        max_length=settings.LENGTH_FIELD_USER_1,
        verbose_name='email',
        unique=True
    )
    username = CharField(
        verbose_name='username',
        max_length=settings.LENGTH_FIELD_USER_2,
        unique=True,
        validators=(UnicodeUsernameValidator(), )
    )

    class Meta:
        ordering = ('username', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(Model):
    """ Подписка на автора """
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        verbose_name='Подписчик',
        related_name='follower',
    )
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        verbose_name='Автор',
        related_name='following'
    )

    class Meta:
        ordering = ('-id', )
        constraints = [
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
            CheckConstraint(
                check=~Q(user=F('author')),
                name='no_self_follow'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return f"{self.user} подписан на {self.author}"
