from django.db import models
from simple_history.models import HistoricForeignKey

from profiles.models import (
    AbstractHistoricalModel,
    AbstractProfile,
    AuthoritativeCharField,
)


class PeopleFinderProfile(AbstractProfile):
    fav_program = AuthoritativeCharField(
        verbose_name="fav_program",
        max_length=255,
        null=True,
        is_authoritative=False,
    )
    super_important = AuthoritativeCharField(
        verbose_name="super_important",
        max_length=255,
        null=True,
        is_authoritative=True,
    )
    team = HistoricForeignKey(
        "PeopleFinderTeam",
        on_delete=models.SET_NULL,
        null=True,
    )


class PeopleFinderTeam(AbstractHistoricalModel):
    name = models.CharField(
        null=True,
    )

    def __str__(self):
        return self.name
