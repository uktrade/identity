from django.db import models
from simple_history.models import HistoricalRecords  # type: ignore

from user.models import User


class AbstractHistoricalModel(models.Model):
    class Meta:
        abstract = True

    history = HistoricalRecords(
        inherit=True,
    )


# @TODO discuss why not inherit from AbstractHistoricalModel
class AbstractProfile(models.Model):
    class Meta:
        abstract = True

    history = HistoricalRecords(
        inherit=True,
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
