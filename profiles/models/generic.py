from enum import StrEnum
from typing import Optional, TypedDict

from django.core.validators import EmailValidator
from django.db import models

from .abstract import AbstractHistoricalModel


class EmailType(StrEnum):
    VERIFIED = "verified"
    CONTACT = "contact"
    USER_ADDED = "user-added"


EmailTypeChoices = [(e.name, e.value) for e in EmailType]


class EmailWithContext(TypedDict):
    address: str
    type: Optional[EmailType]
    preferred: Optional[bool]


class Email(AbstractHistoricalModel):
    address = models.EmailField(validators=[EmailValidator()], unique=True)

    def __str__(self):
        return self.address
