from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


# Create your models here.


class User(AbstractUser):
    sso_email_id = models.CharField(primary_key=True, unique=True)

    objects = UserManager()

    USERNAME_FIELD = "sso_email_id"
    REQUIRED_FIELDS: list[str]

    def __str__(self):
        return self.sso_email_id
