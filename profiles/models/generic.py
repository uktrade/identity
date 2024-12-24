from django.contrib.postgres.fields import ArrayField
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


class Profile(AbstractHistoricalModel):
    sso_email_id = models.CharField(primary_key=True, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    preferred_email = models.CharField(max_length=100)
    emails = ArrayField(models.CharField(max_length=100), default=list)
    is_active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return f"Profile: SSO Email ID: {self.sso_email_id}, First Name: {self.first_name}, Last name: {self.last_name}, Preferred Email: {self.preferred_email}, Emails: {self.emails}"
