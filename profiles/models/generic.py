from django.core.validators import EmailValidator
from django.db import models

from data_flow_s3_import.models import IngestedModel

from .abstract import AbstractHistoricalModel


class Workday(models.TextChoices):
    MON = "MON", "Monday"
    TUE = "TUE", "Tuesday"
    WED = "WED", "Wednesday"
    THU = "THU", "Thursday"
    FRI = "FRI", "Friday"
    SAT = "SAT", "Saturday"
    SUN = "SUN", "Sunday"


class Grade(models.TextChoices):
    FCO_S1 = "FCO_S1", "FCO S1"
    FCO_S2 = "FCO_S2", "FCO S2"
    FCO_S3 = "FCO_S3", "FCO S3"
    ADMIN_ASSISTANT = "ADMIN_ASSISTANT", "Administrative assistant (AA)"
    ADMIN_OFFICER = "ADMIN_OFFICER", "Administrative officer (AO/A2)"
    EXECUTIVE_OFFICER = "EXECUTIVE_OFFICER", "Executive officer (EO/B3)"
    HIGHER_EXECUTIVE_OFFICER = (
        "HIGHER_EXECUTIVE_OFFICER",
        "Higher executive officer (HEO/C4)",
    )
    SENIOR_EXECUTIVE_OFFICER = (
        "SENIOR_EXECUTIVE_OFFICER",
        "Senior executive officer (SEO/C5)",
    )
    GRADE_7 = "GRADE_7", "Grade 7 (G7/D6)"
    GRADE_6 = "GRADE_6", "Grade 6 (G6/D7)"
    SCS_1 = "SCS_1", "Senior civil service 1 (SCS1/SMS1)"
    SCS_2 = "SCS_2", "Senior civil service 2 (SCS2/SMS2)"
    SCS_3 = "SCS_3", "Senior civil service 3 (SCS3/SMS3)"
    SCS_4 = "SCS_4", "Senior civil service 4 (SCS4/SMS4)"
    FAST_STREAM = "FAST_STREAM", "Fast Stream"
    FAST_TRACK = "FAST_TRACK", "Fast Track"
    APPRENTICE = "APPRENTICE", "Apprentice"
    NON_GRADED_SPECIAL_ADVISOR = (
        "NON_GRADED_SPECIAL_ADVISOR",
        "Non graded - special advisor (SPAD)",
    )
    NON_GRADED_CONTRACTOR = "NON_GRADED_CONTRACTOR", "Non graded - contractor"
    NON_GRADED_SECONDEE = "NON_GRADED_SECONDEE", "Non graded - secondee"
    NON_GRADED_POST = "NON_GRADED_POST", "Non graded - post"


class Profession(models.TextChoices):
    COMMERCIAL = "COMMERCIAL", "Government commercial and contract management"
    CORP_FINANCE = "CORP_FINANCE", "Corporate finance profession"
    COUNTER_FRAUD = "COUNTER_FRAUD", "Counter-fraud standards and profession"
    DIGITAL_DATA_TECH = "DIGITAL_DATA_TECH", "Digital, data and technology profession"
    GOV_COMMS = "GOV_COMMS", "Government communication service"
    GOV_ECONOMICS = "GOV_ECONOMICS", "Government economic service"
    GOV_FINANCE = "GOV_FINANCE", "Government finance profession"
    GOV_IT = "GOV_IT", "Government IT profession"
    GOV_KNOWLEDGE = (
        "GOV_KNOWLEDGE",
        "Government knowledge and information management profession",
    )
    GOV_LEGAL = "GOV_LEGAL", "Government legal service"
    GOV_OCCUPATIONAL = (
        "GOV_OCCUPATIONAL",
        "Government occupational psychology profession",
    )
    GOV_OPERATIONAL = "GOV_OPERATIONAL", "Government operational research service"
    GOV_PLANNING_INSPECTORS = (
        "GOV_PLANNING_INSPECTORS",
        "Government planning inspectors",
    )
    GOV_PLANNING_PROFESSION = (
        "GOV_PLANNING_PROFESSION",
        "Government planning profession",
    )
    GOV_PROPERTY = "GOV_PROPERTY", "Government property profession"
    GOV_SECURITY = "GOV_SECURITY", "Government security profession"
    GOV_SCIENCE = "GOV_SCIENCE", "Government science and engineering profession"
    GOV_SOCIAL = "GOV_SOCIAL", "Government social research profession"
    GOV_STATISTICAL = "GOV_STATISTICAL", "Government statistical service profession"
    GOV_TAX = "GOV_TAX", "Government tax profession"
    GOV_VET = "GOV_VET", "Government veterinary profession"
    HUMAN_RESOURCES = "HUMAN_RESOURCES", "Human resources profession"
    INTELLIGENCE_ANALYSIS = "INTELLIGENCE_ANALYSIS", "Intelligence analysis"
    INTERNAL_AUDIT = "INTERNAL_AUDIT", "Internal audit profession"
    MEDICAL_PROFESSION = "MEDICAL_PROFESSION", "Medical profession"
    OPERATION_DELIVERY = "OPERATION_DELIVERY", "Operational delivery profession"
    POLICY_PROFIESSION = "POLICY_PROFIESSION", "Policy profession"
    PROCUREMENT_PROFESSION = "PROCUREMENT_PROFESSION", "Procurement profession"
    PROJECT_DELIVERY = "PROJECT_DELIVERY", "Project delivery profession"
    INTERNATIONAL_TRADE = "INTERNATIONAL_TRADE", "International trade profession"


class Email(AbstractHistoricalModel):
    address = models.EmailField(validators=[EmailValidator()], unique=True)

    def __str__(self):
        return self.address


class Country(IngestedModel):
    """
    Country model populated by the Data Workspace country datasetfound here:
    https://data.trade.gov.uk/datasets/240d5034-6a83-451b-8307-5755672f881b#countries-territories-and-regions.
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
    overseas_region = models.CharField(max_length=40, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name


class UkStaffLocation(IngestedModel):
    """
    UkStaffLocation model populated by the Data Workspace DBT Staff Locations datasetfound here:
    https://data.trade.gov.uk/datasets/e89b0647-9b83-48ae-9234-0fccd6b90fa4#dit-staff-locations.
    """

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["code"], name="unique_location_code"),
        ]
        indexes = [
            models.Index(fields=["code"]),
        ]
        ordering = ["name"]

    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    organisation = models.CharField(max_length=255)
    building_name = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return self.name
