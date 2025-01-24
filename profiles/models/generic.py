from django.core.validators import EmailValidator
from django.db import models
from django.urls import reverse

from .abstract import AbstractHistoricalModel, IngestedModel


class Email(AbstractHistoricalModel):
    address = models.EmailField(validators=[EmailValidator()], unique=True)

    def __str__(self):
        return self.address


# markdown
DEFAULT_TEAM_DESCRIPTION = """Find out who is in the team and their contact details.

You can update this description, by [updating your team information](https://workspace.trade.gov.uk/working-at-dbt/how-do-i/update-my-team-information-on-people-finder/).
"""


class Team(AbstractHistoricalModel):
    class LeadersOrdering(models.TextChoices):
        ALPHABETICAL = "alphabetical", "Alphabetical"
        CUSTOM = "custom", "Custom"

    slug = models.SlugField(max_length=130, unique=True, editable=True)
    name = models.CharField(
        "Team name (required)",
        max_length=255,
        help_text="The full name of this team (e.g. Digital, Data and Technology)",
    )
    abbreviation = models.CharField(
        "Team acronym or initials",
        max_length=20,
        null=True,
        blank=True,
        help_text="A short form of the team name, up to 10 characters. For example DDaT.",
    )
    description = models.TextField(
        "Team description",
        null=False,
        blank=False,
        default=DEFAULT_TEAM_DESCRIPTION,
        help_text="What does this team do? Use Markdown to add lists and links. Enter up to 1500 characters.",
    )
    leaders_ordering = models.CharField(
        max_length=12,
        choices=LeadersOrdering.choices,
        default=LeadersOrdering.ALPHABETICAL,
        blank=True,
    )

    def __str__(self) -> str:
        return self.short_name

    def get_absolute_url(self) -> str:
        return reverse("team-view", kwargs={"slug": self.slug})

    @property
    def short_name(self) -> str:
        """Return a short name for the team.

        Returns:
            str: The team's short name.
        """
        return self.abbreviation or self.name


class Country(models.Model):
    """
    Country model for use with the Data Workspace country dataset.

    Information about the dataset can be found here:
    https://data.trade.gov.uk/datasets/240d5034-6a83-451b-8307-5755672f881b#countries-territories-and-regions.

    The data required to populate this model can be downloaded from here:
    https://data.trade.gov.uk/datasets/240d5034-6a83-451b-8307-5755672f881b/grid.

    Use the provided `generate_countries_fixture` management command to produce a
    fixture which is compatible with this model.

    This model was built against the 5.35 version of the dataset.
    """

    class Meta:
        verbose_name_plural = "countries"

    class Type(models.TextChoices):
        COUNTRY = "country", "Country"
        TERRITORY = "territory", "Territory"

    reference_id = models.CharField("Reference ID", primary_key=True, max_length=11)
    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=9, choices=Type.choices)
    iso_1_code = models.CharField("ISO 1 Code", max_length=3, unique=True)
    iso_2_code = models.CharField("ISO 2 Code", max_length=2, unique=True)
    iso_3_code = models.CharField("ISO 3 Code", max_length=3, unique=True)
    overseas_region = models.CharField(max_length=40, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    def __str__(self):
        return self.name


class WorkdayQuerySet(models.QuerySet):
    def all_mon_to_sun(self):
        codes = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

        return sorted(self.all(), key=lambda x: codes.index(x.code))


class Workday(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["code"], name="unique_workday_code"),
            models.UniqueConstraint(fields=["name"], name="unique_workday_name"),
        ]

    code = models.CharField(max_length=3)
    name = models.CharField(max_length=9)

    objects = WorkdayQuerySet.as_manager()

    def __str__(self) -> str:
        return self.name


class Grade(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["code"], name="unique_grade_code"),
            models.UniqueConstraint(fields=["name"], name="unique_grade_name"),
        ]
        ordering = ["name"]

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name


class KeySkill(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["code"], name="unique_key_skill_code"),
            models.UniqueConstraint(fields=["name"], name="unique_key_skill_name"),
        ]
        ordering = ["name"]

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name


class Profession(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["code"], name="unique_profession_code"),
            models.UniqueConstraint(fields=["name"], name="unique_profession_name"),
        ]
        ordering = ["name"]

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=60)

    def __str__(self) -> str:
        return self.name


class UkStaffLocation(IngestedModel):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["code"], name="unique_location_code"),
        ]
        ordering = ["name"]

    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    organisation = models.CharField(max_length=255)
    building_name = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return self.name
