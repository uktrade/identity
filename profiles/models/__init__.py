from django.db import models


class ProfileTypes(models.TextChoices):
    STAFF_SSO = "SSO", "Staff SSO"
    PEOPLE_FINDER = "PF", "People Finder"
    ORACLE = "ORACLE", "Oracle"
