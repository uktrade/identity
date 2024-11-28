from django.db import models


class User(models.Model):
    ...


class Proifle(models.Model):
    user: User

class StaffSSOProfile(Proifle):
    user: User
    sso_id: int
    given_name: str
    family_name: str
    prefered_email: str
    emails: list[str]


class PeopleFinderProfile(Proifle):
    user: User
    first_name: str
    last_name: str
    prefered_email: str
    emails: list[str]