import uuid
from random import choice
from typing import Iterator

from django.db import models
from django.db.models import F, Q
from django.utils.safestring import mark_safe
from django_chunk_upload_handlers.clam_av import validate_virus_check_result

from core.models import ChoiceArrayField
from profiles.models.abstract import AbstractHistoricalModel
from profiles.models.generic import Grade, Profession, Workday


# United Kingdom
DEFAULT_COUNTRY_PK = "CTHMTC00260"


def person_photo_path(instance, filename):
    return f"peoplefinder/person/{instance.slug}/photo/{filename}"


def person_photo_small_path(instance, filename):
    return f"peoplefinder/person/{instance.slug}/photo/small_{filename}"


class LearningInterest(models.TextChoices):
    SHADOWING = "Work shadowing"
    MENTORING = "Mentoring"
    RESEARCH = "Research"
    OVERSEAS_POSTS = "Overseas posts"
    SECONDMENT = "Secondment"
    PARLIAMENTARY_WORK = "Parliamentary work"
    MINISTERIAL_SUBMISSIONS = "Ministerial submissions"
    CODING = "Coding"


class KeySkill(models.TextChoices):
    ASSET_MANAGEMENT = "Asset management"
    ASSURANCE = "Assurance"
    BENEFITS_REALISATION = "Benefits realisation"
    CHANGE_MANAGEMENT = "Change management"
    COACHING = "Coaching"
    COMMERCIAL_SPECIALIST = "Commercial specialist"
    COMMISSIONING = "Commissioning"
    CONTRACT_MANAGEMENT = "Contract management"
    CREDIT_RISK_ANALYSIS = "Credit risk analysis"
    CUSTOMER_SERVICE = "Customer service"
    DIGITAL = "Digital"
    DIGITAL_WORKSPACE_PUBLISHER = "Digital Workspace publisher"
    ECONOMIST = "Economist"
    FINANCIAL_REPORTING = "Financial reporting"
    GRAPHIC_DESIGN = "Graphic Design"
    HR = "HR"
    INCOME_GENERATION = "Income generation"
    INFORMATION_MANAGEMENT = "Information management"
    INTERVIEWING = "Interviewing"
    IT = "IT"
    LAW = "Law"
    LEAN = "Lean/ Six sigma"
    LINE_MANAGEMENT = "Line management"
    MEDIA_TRAINED = "Media trained"
    MENTORING = "Mentoring"
    POLICY_DESIGN = "Policy design"
    POLICY_IMPLEMENTATION = "Policy implementation"
    PRESENTING = "Presenting"
    PROJECT_DELIVERY = "Project delivery"
    PROJECT_MANAGEMENT = "Project management"
    PROPERTY_ESTATES = "Property / Estates"
    RESEARCH_OPERATIONAL = "Research - operational"
    RESEARCH_ECONOMIC = "Research - economic"
    RESEARCH_STATISTICAL = "Research - statistical"
    RESEARCH_SOCIAL = "Research - social"
    RISK_MANAGEMENT = "Risk management"
    SECURITY = "Security"
    SERVICE_DESIGN = "Service and process design"
    SKILLS_AND_CAPABILITY = "Skills and capability management"
    SPONSORSHIP = "Sponsorship and partnerships"
    STAKEHOLDER_MANAGEMENT = "Stakeholder management"
    STATISTICS = "Statistics"
    STRATEGY = "Strategy"
    SUBMISSION_WRITING = "Submission writing"
    TALENT_MANAGEMENT = "Talent Management"
    TAX = "Tax"
    TRAINING = "Training"
    UNDERWRITING = "Underwriting"
    USER_RESEARCH = "User research"
    VALUTION = "Valuation"
    WORKING_WITH_DEVOLVED_ADMIN = "Working with Devolved Administrations"
    WORKING_WITH_MINISTERS = "Working with Ministers"
    WORKING_WITH_GOVT_DEPTS = "Working with other government departments"


class AdditionalRole(models.TextChoices):
    FIRE_WARDEN = "Fire warden"
    FIRST_AIDER = "First aider"
    MENTAL_HEALTH_FIRST_AIDER = "Mental health first aider"
    MENTOR = "Mentor"
    NETWORK_LEAD = "Network lead"
    NETWORK_DEPUTY_LEAD = "Network deputy lead"
    CIRRUS_CHAMPION = "Cirrus champion"
    HEALTH_WELLBEING_CHAMPION = "Health & wellbeing champion"
    FAST_STREAM_REP = "Fast stream rep"
    OVERSEAS_STAFF_REP = "Overseas staff rep"
    DIGITAL_CHAMPION = "Digital champion"
    INFORMATION_MANAGER = "Information manager"
    INDEPENDENT_PANEL_MEMBER = "Independent panel member"
    DIVISIONAL_SECURITY_COORDINATOR = "Divisional security coordinator"
    DDAT_CHAMPION = "DDaT champion"
    HONOURS_CHAMPION = "Honours champion"


class RemoteWorking(models.TextChoices):
    OFFICE_WORKER = "office_worker"
    REMOTE_WORKER = "remote_worker"
    SPLIT = "split"


class PeopleFinderProfile(AbstractHistoricalModel):
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~Q(id=F("manager")), name="manager_cannot_be_self"
            ),
        ]
        indexes = [
            models.Index(fields=["slug"]),
        ]

    slug = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.OneToOneField(
        "user.User", models.CASCADE, null=True, blank=True, related_name="profile"
    )

    # Basic Profile info
    #
    first_name = models.CharField(
        max_length=200,
    )
    preferred_first_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    last_name = models.CharField(
        max_length=200,
    )
    pronouns = models.CharField(max_length=40, null=True, blank=True)
    name_pronunciation = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    email = models.ForeignKey(
        "profiles.Email",
        models.SET_NULL,
        null=True,
        related_name="+",
    )
    contact_email = models.ForeignKey(
        "profiles.Email",
        models.SET_NULL,
        null=True,
        related_name="+",
    )
    primary_phone_number = models.CharField(
        max_length=42,
        null=True,
        blank=True,
    )
    secondary_phone_number = models.CharField(
        max_length=160,
        null=True,
        blank=True,
    )
    photo = models.ImageField(
        max_length=255,
        null=True,
        blank=True,
        upload_to=person_photo_path,
        validators=[validate_virus_check_result],
    )
    photo_small = models.ImageField(
        max_length=255,
        null=True,
        blank=True,
        upload_to=person_photo_small_path,
        validators=[validate_virus_check_result],
    )

    # HR information
    #
    grade = models.CharField(
        null=True, blank=True, max_length=80, choices=Grade.choices
    )
    manager = models.ForeignKey(
        "PeopleFinderProfile",
        models.SET_NULL,
        null=True,
        blank=True,
        related_name="direct_reports",
    )
    not_employee = models.BooleanField(
        "Non-direct employee, implies no manager listed", default=False
    )

    # Working patterns
    #
    workdays = ChoiceArrayField(
        base_field=models.CharField(
            verbose_name="Usual work days",
            null=True,
            blank=True,
            max_length=80,
            choices=Workday.choices,
        ),
        null=True,
        blank=True,
    )
    remote_working = models.CharField(
        verbose_name="Usual working location",
        blank=True,
        null=True,
        max_length=80,
        choices=RemoteWorking.choices,
    )
    usual_office_days = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    uk_office_location = models.ForeignKey(
        "UkStaffLocation",
        verbose_name="Contracted office location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    location_in_building = models.CharField(
        max_length=130,
        null=True,
        blank=True,
    )
    international_building = models.CharField(
        "International location",
        max_length=110,
        null=True,
        blank=True,
        help_text="Complete if you work outside the UK",
    )
    country = models.ForeignKey(
        "profiles.Country",
        models.PROTECT,
        default=DEFAULT_COUNTRY_PK,  #  type: ignore
        related_name="+",
    )

    # Supplementary info
    #
    professions = ChoiceArrayField(
        base_field=models.CharField(
            blank=True,
            choices=Profession.choices,
        ),
        null=True,
        blank=True,
    )
    additional_roles = ChoiceArrayField(
        base_field=models.CharField(
            verbose_name="Additional roles or responsibilities",
            blank=True,
            choices=AdditionalRole.choices,
        ),
        null=True,
        blank=True,
    )
    other_additional_roles = models.CharField(
        max_length=400,
        null=True,
        blank=True,
        help_text="Use a comma to separate multiple values.",
    )
    key_skills = ChoiceArrayField(
        models.CharField(
            blank=True,
            choices=KeySkill.choices,
        ),
        null=True,
        blank=True,
    )
    other_key_skills = models.CharField(
        max_length=700,
        null=True,
        blank=True,
        help_text="Use a comma to separate multiple values.",
    )
    learning_interests = ChoiceArrayField(
        models.CharField(
            blank=True,
            choices=LearningInterest.choices,
        ),
        null=True,
        blank=True,
    )
    other_learning_interests = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Use a comma to separate multiple values.",
    )
    fluent_languages = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Use a comma to separate multiple values.",
    )
    intermediate_languages = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    previous_experience = models.TextField(
        null=True,
        blank=True,
    )

    # Metadata and status
    #
    is_active = models.BooleanField(default=True)
    became_inactive = models.DateTimeField(null=True, blank=True)
    edited_or_confirmed_at = models.DateTimeField()
    login_count = models.IntegerField(default=0)
    profile_completion = models.IntegerField(default=0)
    ical_token = models.CharField(
        verbose_name="Individual token for iCal feeds",
        blank=True,
        null=True,
        max_length=80,
    )

    def __str__(self) -> str:
        return self.full_name

    def save(self, *args, **kwargs):
        from profiles.services import peoplefinder

        self.profile_completion = 10
        # TODO: Implement get_profile_completion() funtion.
        # peoplefinder.get_profile_completion(
        #     peoplefinder_profile=self
        # )
        return super().save(*args, **kwargs)

    @property
    def full_name(self) -> str:
        first_name = self.first_name
        if self.preferred_first_name:
            first_name = self.preferred_first_name
        return f"{first_name} {self.last_name}"

    @property
    def is_line_manager(self) -> bool:
        return self.direct_reports.exists()  # type: ignore

    @property
    def has_photo(self) -> bool:
        return bool(self.photo)


class PeopleFinderTeamLeadersOrdering(models.TextChoices):
    ALPHABETICAL = "alphabetical", "Alphabetical"
    CUSTOM = "custom", "Custom"


class PeopleFinderTeamTypes(models.TextChoices):
    STANDARD = "Standard"
    DIRECTORATE = "Directorate"
    PORTFOLIO = "Portfolio"


class PeopleFinderTeam(AbstractHistoricalModel):
    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
        ]

    slug = models.SlugField(max_length=130, unique=True, editable=True)
    name = models.CharField(
        max_length=255,
    )
    abbreviation = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )
    description = models.TextField(
        null=True,
        blank=True,
        default=None,
    )
    leaders_ordering = models.CharField(
        max_length=12,
        choices=PeopleFinderTeamLeadersOrdering.choices,
        default=PeopleFinderTeamLeadersOrdering.ALPHABETICAL,
        blank=True,
    )
    cost_code = models.CharField(
        "Financial cost code associated with this team",
        max_length=20,
        null=True,
        blank=True,
    )
    team_type = models.CharField(
        max_length=20,
        choices=PeopleFinderTeamTypes.choices,
        default=PeopleFinderTeamTypes.STANDARD,
        blank=True,
    )

    def __str__(self) -> str:
        return self.short_name

    @property
    def short_name(self) -> str:
        return self.abbreviation or self.name


class PeopleFinderProfileTeam(AbstractHistoricalModel):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["peoplefinder_profile", "team", "job_title", "head_of_team"],
                name="unique_team_member",
            ),
        ]

    peoplefinder_profile = models.ForeignKey(
        PeopleFinderProfile,
        models.CASCADE,
        related_name="roles",
    )
    team = models.ForeignKey(
        PeopleFinderTeam,
        models.CASCADE,
        related_name="peoplefinder_members",
    )
    job_title = models.CharField(max_length=255)
    head_of_team = models.BooleanField(default=False)
    leaders_position = models.SmallIntegerField(null=True)

    def __str__(self) -> str:
        return f"{self.team} - {self.peoplefinder_profile}"


class PeopleFinderTeamTree(AbstractHistoricalModel):
    class Meta:
        unique_together = [["parent", "child"]]

    parent = models.ForeignKey(
        PeopleFinderTeam,
        models.CASCADE,
        related_name="parents",
    )
    child = models.ForeignKey(
        PeopleFinderTeam,
        models.CASCADE,
        related_name="children",
    )

    depth = models.SmallIntegerField()

    def __str__(self) -> str:
        return f"{self.parent} - {self.child} ({self.depth})"
