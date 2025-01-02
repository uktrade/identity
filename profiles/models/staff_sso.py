from django.db import models

from .abstract import AbstractHistoricalModel, AbstractProfile
from .generic import Email, EmailType, EmailTypeChoices


class StaffSSOProfile(AbstractProfile):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    @property
    def contact_email(self):
        try:
            return self.emails.get(type=EmailType.CONTACT, preferred=True)
        except StaffSSOProfileEmail.DoesNotExist:
            try:
                return self.emails.get(type=EmailType.CONTACT)
            except StaffSSOProfileEmail.DoesNotExist:
                return None

    @property
    def email_addresses(self):
        return [e["email__address"] for e in self.emails.values("email__address")]

    def __str__(self):
        return f"StaffSSOProfile: {self.first_name} {self.last_name}"


class StaffSSOProfileEmail(AbstractHistoricalModel):
    profile = models.ForeignKey(
        "StaffSSOProfile", on_delete=models.CASCADE, related_name="emails"
    )
    email = models.ForeignKey(Email, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=EmailTypeChoices)
    preferred = models.BooleanField(default=False)

    class Meta:
        unique_together = ("profile", "email", "type", "preferred")

    def __str__(self):
        return f"StaffSSOProfileEmail: {self.profile.first_name} {self.profile.last_name}: {self.email.address}"
