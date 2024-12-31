from django.core.validators import EmailValidator
from django.db import models

from .abstract import AbstractHistoricalModel


class EmailTypes(models.TextChoices):
    WORK = "work", "Work"
    CONTACT = "contact", "Contact"


class Email(AbstractHistoricalModel):
    address = models.EmailField(validators=[EmailValidator()], unique=True)

    def __str__(self):
        return self.address
