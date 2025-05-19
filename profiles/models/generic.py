from data_flow_s3_import.models import IngestedModel
from django.core.validators import EmailValidator
from django.db import models

from .abstract import AbstractHistoricalModel


class Workday(models.TextChoices):
    MON = "mon", "Monday"
    TUE = "tue", "Tuesday"
    WED = "wed", "Wednesday"
    THU = "thu", "Thursday"
    FRI = "fri", "Friday"
    SAT = "sat", "Saturday"
    SUN = "sun", "Sunday"


class Grade(models.TextChoices):
    FCO_S1 = "fco_s1", "FCO S1"
    FCO_S2 = "fco_s2", "FCO S2"
    FCO_S3 = "fco_s3", "FCO S3"
    ADMIN_ASSISTANT = "admin_assistant", "Administrative assistant (AA)"
    ADMIN_OFFICER = "admin_officer", "Administrative officer (AO/A2)"
    EXECUTIVE_OFFICER = "executive_officer", "Executive officer (EO/B3)"
    HIGHER_EXECUTIVE_OFFICER = (
        "higher_executive_officer",
        "Higher executive officer (HEO/C4)",
    )
    SENIOR_EXECUTIVE_OFFICER = (
        "senior_executive_officer",
        "Senior executive officer (SEO/C5)",
    )
    GRADE_7 = "grade_7", "Grade 7 (G7/D6)"
    GRADE_6 = "grade_6", "Grade 6 (G6/D7)"
    SCS_1 = "scs_1", "Senior civil service 1 (SCS1/SMS1)"
    SCS_2 = "scs_2", "Senior civil service 2 (SCS2/SMS2)"
    SCS_3 = "scs_3", "Senior civil service 3 (SCS3/SMS3)"
    SCS_4 = "scs_4", "Senior civil service 4 (SCS4/SMS4)"
    FAST_STREAM = "fast_stream", "Fast Stream"
    FAST_TRACK = "fast_track", "Fast Track"
    APPRENTICE = "apprentice", "Apprentice"
    NON_GRADED_SPECIAL_ADVISOR = (
        "non_graded_special_advisor",
        "Non graded - special advisor (SPAD)",
    )
    NON_GRADED_CONTRACTOR = "non_graded_contractor", "Non graded - contractor"
    NON_GRADED_SECONDEE = "non_graded_secondee", "Non graded - secondee"
    NON_GRADED_POST = "non_graded_post", "Non graded - post"


class Profession(models.TextChoices):
    COMMERCIAL = "commercial", "Government commercial and contract management"
    CORP_FINANCE = "corp_finance", "Corporate finance profession"
    COUNTER_FRAUD = "counter_fraud", "Counter-fraud standards and profession"
    DIGITAL_DATA_TECH = "digital_data_tech", "Digital, data and technology profession"
    GOV_COMMS = "gov_comms", "Government communication service"
    GOV_ECONOMICS = "gov_economics", "Government economic service"
    GOV_FINANCE = "gov_finance", "Government finance profession"
    GOV_IT = "gov_it", "Government IT profession"
    GOV_KNOWLEDGE = (
        "gov_knowledge",
        "Government knowledge and information management profession",
    )
    GOV_LEGAL = "gov_legal", "Government legal service"
    GOV_OCCUPATIONAL = (
        "gov_occupational",
        "Government occupational psychology profession",
    )
    GOV_OPERATIONAL = "gov_operational", "Government operational research service"
    GOV_PLANNING_INSPECTORS = (
        "gov_planning_inspectors",
        "Government planning inspectors",
    )
    GOV_PLANNING_PROFESSION = (
        "gov_planning_profession",
        "Government planning profession",
    )
    GOV_PROPERTY = "gov_property", "Government property profession"
    GOV_SECURITY = "gov_security", "Government security profession"
    GOV_SCIENCE = "gov_science", "Government science and engineering profession"
    GOV_SOCIAL = "gov_social", "Government social research profession"
    GOV_STATISTICAL = "gov_statistical", "Government statistical service profession"
    GOV_TAX = "gov_tax", "Government tax profession"
    GOV_VET = "gov_vet", "Government veterinary profession"
    HUMAN_RESOURCES = "human_resources", "Human resources profession"
    INTELLIGENCE_ANALYSIS = "intelligence_analysis", "Intelligence analysis"
    INTERNAL_AUDIT = "internal_audit", "Internal audit profession"
    MEDICAL_PROFESSION = "medical_profession", "Medical profession"
    OPERATION_DELIVERY = "operation_delivery", "Operational delivery profession"
    POLICY_PROFIESSION = "policy_profiession", "Policy profession"
    PROCUREMENT_PROFESSION = "procurement_profession", "Procurement profession"
    PROJECT_DELIVERY = "project_delivery", "Project delivery profession"
    INTERNATIONAL_TRADE = "international_trade", "International trade profession"


class Email(AbstractHistoricalModel):
    address = models.EmailField(validators=[EmailValidator()], unique=True)

    def __str__(self):
        return self.address


class Country(IngestedModel):
    """
    Country model is populated by the Data Workspace country dataset found here:
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
    UkStaffLocation model is populated by the Data Workspace DBT Staff Locations dataset found here:
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


class SectorList(IngestedModel):
    """
    SectorList model is populated by the Data Workspace DBT Sector List dataset found here:
    https://data.trade.gov.uk/datasets/5c67e06c-5456-40db-b93c-26043f972996
    """

    sector_id = models.CharField(max_length=255, unique=True)
    full_sector_name = models.CharField(max_length=255)
    sector_cluster_name_april_2023_onwards = models.CharField(max_length=255)
    sector_cluster_name_before_april_2023 = models.CharField(max_length=255)
    sector_name = models.CharField(max_length=255)
    sub_sector_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    sub_sub_sector_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    start_date = models.DateField(
        null=True,
        blank=True,
    )
    end_date = models.DateField(
        null=True,
        blank=True,
    )
