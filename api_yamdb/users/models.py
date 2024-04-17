from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Класс переопределяет и расширяет стандартную модель User."""

    USERNAME_ERR_MESS = (
        "Содержание поля 'username' не соответствует "
        "паттерну '^[\\w.@+-]+\\z'"
    )

    username = models.CharField(
        max_length=150,
        blank=False,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+\Z",
                message=USERNAME_ERR_MESS,
            )
        ],
    )
    email = models.EmailField(
        blank=False,
        unique=True,
        max_length=254,
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )
