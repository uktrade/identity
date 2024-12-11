from django.contrib.auth.models import AbstractUser
from django.db import models



# Create your models here.


class User(AbstractUser):
    sso_email_id = models.CharField(primary_key=True, unique=True)
    USERNAME_FIELD = "sso_email_id"

    def __str__(self):
        return self.sso_email_id
