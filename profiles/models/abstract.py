from django.db import models
from simple_history.models import HistoricalRecords  # type: ignore

from user.models import User


class AbstractHistoricalModel(models.Model):
    class Meta:
        abstract = True

    history = HistoricalRecords(
        inherit=True,
    )


class AbstractProfile(models.Model):
    class Meta:
        abstract = True

    history = HistoricalRecords(
        inherit=True,
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)

    @property
    def sso_email_id(self):
        return self.user.sso_email_id


class IngestedModelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class IngestedModel(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    objects = IngestedModelManager()
