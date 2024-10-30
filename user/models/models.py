from django.contrib.auth.models import AbstractUser
from django.db import models
from simple_history.models import HistoricalRecords


# Create your models here.
class User(AbstractUser):
    history = HistoricalRecords()

    def __str__(self):
        return f"({self.username}) {self.first_name} {self.last_name}"
