from django.db import models

from .abstract import AbstractHistoricalModel, AbstractProfile
from .generic import EMAIL_TYPES, Email


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
