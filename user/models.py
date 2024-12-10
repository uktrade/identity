from django.contrib.auth.models import AbstractBaseUser, AbstractUser, PermissionsMixin
from django.db import models

from .managers import UserManager


# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"

    sso_email_id = models.CharField(primary_key=True, unique=True)

    is_staff = models.BooleanField(
        default=False,
    )
    is_active = models.BooleanField(
        default=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "sso_email_id"
    REQUIRED_FIELDS: list[str]

    def __str__(self):
        return self.sso_email_id
