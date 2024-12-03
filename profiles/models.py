from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.validators import EmailValidator
from django.db import models


User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )


class StaffSSOProfile(Profile):
    sso_id = models.IntegerField(unique=True)
    given_name = models.CharField(max_length=100)
    family_name = models.CharField(max_length=100)
    preferred_email = models.EmailField(validators=[EmailValidator()])
    emails = ArrayField(
        models.EmailField(validators=[EmailValidator()]), blank=True, default=list
    )


class PeopleFinderProfile(Profile):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    preferred_email = models.EmailField(validators=[EmailValidator()])
    emails = ArrayField(
        models.EmailField(validators=[EmailValidator()]), blank=True, default=list
    )
