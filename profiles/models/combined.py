from django.contrib.postgres.fields import ArrayField
from django.db import models

from .abstract import AbstractHistoricalModel


class Profile(AbstractHistoricalModel):
    sso_email_id = models.CharField(primary_key=True, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    primary_email = models.CharField(max_length=100)
    contact_email = models.CharField(max_length=100, null=True, blank=True)
    emails = ArrayField(models.CharField(max_length=100), default=list)
    is_active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
