from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Profile(models.Model):
    user: User


class StaffSSOProfile(Profile):
    user: User
    sso_id: int
    given_name: str
    family_name: str
    prefered_email: str
    emails: list[str]


class PeopleFinderProfile(Profile):
    user: User
    first_name: str
    last_name: str
    prefered_email: str
    emails: list[str]
