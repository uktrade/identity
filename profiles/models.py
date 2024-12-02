from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import EmailField

User = get_user_model()


class Profile(models.Model):
    user: User


class StaffSSOProfile(Profile):
    sso_id: int
    given_name: str
    family_name: str
    preferred_email: EmailField
    emails: ArrayField(EmailField)


class PeopleFinderProfile(Profile):
    first_name: str
    last_name: str
    preferred_email: EmailField
    emails: ArrayField(EmailField)
