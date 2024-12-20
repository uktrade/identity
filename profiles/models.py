from django.contrib.postgres.fields import ArrayField
from django.core.validators import EmailValidator
from django.db import models
from simple_history.models import HistoricalRecords  # type: ignore

from user.models import User


EMAIL_TYPE_WORK = "work"
EMAIL_TYPE_CONTACT = "contact"
EMAIL_TYPES = ((EMAIL_TYPE_WORK, "Work"), (EMAIL_TYPE_CONTACT, "Contact"))


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


class StaffSSOProfile(AbstractProfile):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"First Name: {self.first_name}, Last Name: {self.last_name}"


class StaffSSOProfileEmail(AbstractHistoricalModel):
    profile = models.ForeignKey(
        "StaffSSOProfile", on_delete=models.CASCADE, related_name="emails"
    )
    email = models.ForeignKey(Email, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=EMAIL_TYPES)
    preferred = models.BooleanField(default=False)

    class Meta:
        unique_together = ("profile", "email", "type")

    def __str__(self):
        return f"Profile: {self.profile.__str__()} - Email: {self.email.__str__()} - Email Type: {self.type} Preferred: {self.preferred}"
