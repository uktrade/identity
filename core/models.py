from django.contrib.postgres.fields import ArrayField
from django.db import models


class User(models.Model):
    external_id: str


class Email(models.Model):
    address = models.EmailField()


class Proifle(models.Model):
    user: User


class StaffSSOProfile(Proifle):
    user: User
    sso_id: int
    given_name: str
    family_name: str
    prefered_email = models.EmailField()
    emails = ArrayField(Email)


class PeopleFinderProfile(Proifle):
    first_name: str
    last_name: str
    prefered_email = models.EmailField()
    emails = ArrayField(Email)
