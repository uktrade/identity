from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models


# Create your models here.


class UserManager(BaseUserManager):
    def _create_user(
        self, sso_email_id: str, password: str | None = None, **extra_fields
    ):
        if not sso_email_id:
            raise ValueError("The sso_email_id must be set")
        user = self.model(sso_email_id=sso_email_id, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(
        self, sso_email_id: str, password: str | None = None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(sso_email_id, password, **extra_fields)

    def create_superuser(self, sso_email_id: str, password: str, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(sso_email_id, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

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
