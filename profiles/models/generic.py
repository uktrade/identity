from django.core.validators import EmailValidator
from django.db import models

from .abstract import AbstractHistoricalModel


class Email(AbstractHistoricalModel):
    address = models.EmailField(validators=[EmailValidator()], unique=True)

    def __str__(self):
        return self.address
