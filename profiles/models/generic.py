from django.core.validators import EmailValidator
from django.db import models

from .abstract import AbstractHistoricalModel


class EmailTypes(models.TextChoices):
    VERIFIED = "verified", "Auth verified"
    CONTACT = "contact", "Contact"
    USER_ADDED = "user-added", "User added"


class Email(AbstractHistoricalModel):
    address = models.EmailField(validators=[EmailValidator()], unique=True)

    def __str__(self):
        return self.address
