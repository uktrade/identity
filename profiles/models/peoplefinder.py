import uuid
from typing import Optional, TypedDict

from django.db import models
from django.db.models import F, Q
from django_chunk_upload_handlers.clam_av import validate_virus_check_result

from core.models import ChoiceArrayField
from profiles.models.abstract import AbstractHistoricalModel
from profiles.models.generic import Grade, Profession, Workday


# United Kingdom
DEFAULT_COUNTRY_PK = "CTHMTC00260"


def person_photo_path(instance, filename):
    return f"profiles/{instance.slug}/photo/{filename}"


def person_photo_small_path(instance, filename):
    return f"profiles/{instance.slug}/photo/small_{filename}"


class LearningInterest(models.TextChoices):
    SHADOWING = "shadowing", "Work shadowing"
    MENTORING = "mentoring", "Mentoring"
    RESEARCH = "research", "Research"
    OVERSEAS_POSTS = "overseas_posts", "Overseas posts"
    SECONDMENT = "secondment", "Secondment"
    PARLIAMENTARY_WORK = "parliamentary_work", "Parliamentary work"
    MINISTERIAL_SUBMISSIONS = "ministerial_submissions", "Ministerial submissions"
    CODING = "coding", "Coding"


class KeySkill(models.TextChoices):
    ASSET_MANAGEMENT = "asset_management", "Asset management"
    ASSURANCE = "assurance", "Assurance"
    BENEFITS_REALISATION = "benefits_realisation", "Benefits realisation"
    CHANGE_MANAGEMENT = "change_management", "Change management"
    COACHING = "coaching", "Coaching"
    COMMERCIAL_SPECIALIST = "commercial_specialist", "Commercial specialist"
    COMMISSIONING = "commissioning", "Commissioning"
    CONTRACT_MANAGEMENT = "contract_management", "Contract management"
    CREDIT_RISK_ANALYSIS = "credit_risk_analysis", "Credit risk analysis"
    CUSTOMER_SERVICE = "customer_service", "Customer service"
    DIGITAL = "digital", "Digital"
    DIGITAL_WORKSPACE_PUBLISHER = (
        "digital_workspace_publisher",
        "Digital Workspace publisher",
    )
    ECONOMIST = "economist", "Economist"
    FINANCIAL_REPORTING = "financial_reporting", "Financial reporting"
    GRAPHIC_DESIGN = "graphic_design", "Graphic Design"
    HR = "hr", "HR"
    INCOME_GENERATION = "income_generation", "Income generation"
    INFORMATION_MANAGEMENT = "information_management", "Information management"
    INTERVIEWING = "interviewing", "Interviewing"
    IT = "it", "IT"
    LAW = "law", "Law"
    LEAN = "lean", "Lean/ Six sigma"
    LINE_MANAGEMENT = "line_management", "Line management"
    MEDIA_TRAINED = "media_trained", "Media trained"
    MENTORING = "mentoring", "Mentoring"
    POLICY_DESIGN = "policy_design", "Policy design"
    POLICY_IMPLEMENTATION = "policy_implementation", "Policy implementation"
    PRESENTING = "presenting", "Presenting"
    PROJECT_DELIVERY = "project_delivery", "Project delivery"
    PROJECT_MANAGEMENT = "project_management", "Project management"
    PROPERTY_ESTATES = "property_estates", "Property / Estates"
    RESEARCH_OPERATIONAL = "research_operational", "Research - operational"
    RESEARCH_ECONOMIC = "research_economic", "Research - economic"
    RESEARCH_STATISTICAL = "research_statistical", "Research - statistical"
    RESEARCH_SOCIAL = "research_social", "Research - social"
    RISK_MANAGEMENT = "risk_management", "Risk management"
    SECURITY = "security", "Security"
    SERVICE_DESIGN = "service_design", "Service and process design"
    SKILLS_AND_CAPABILITY = "skills_and_capability", "Skills and capability management"
    SPONSORSHIP = "sponsorship", "Sponsorship and partnerships"
    STAKEHOLDER_MANAGEMENT = "stakeholder_management", "Stakeholder management"
    STATISTICS = "statistics", "Statistics"
    STRATEGY = "strategy", "Strategy"
    SUBMISSION_WRITING = "submission_writing", "Submission writing"
    TALENT_MANAGEMENT = "talent_management", "Talent Management"
    TAX = "tax", "Tax"
    TRAINING = "training", "Training"
    UNDERWRITING = "underwriting", "Underwriting"
    USER_RESEARCH = "user_research", "User research"
    VALUTION = "valution", "Valuation"
    WORKING_WITH_DEVOLVED_ADMIN = (
        "working_with_devolved_admin",
        "Working with Devolved Administrations",
    )
    WORKING_WITH_MINISTERS = "working_with_ministers", "Working with Ministers"
    WORKING_WITH_GOVT_DEPTS = (
        "working_with_govt_depts",
        "Working with other government departments",
    )


class AdditionalRole(models.TextChoices):
    FIRE_WARDEN = "fire_warden", "Fire warden"
    FIRST_AIDER = "first_aider", "First aider"
    MENTAL_HEALTH_FIRST_AIDER = "mental_health_first_aider", "Mental health first aider"
    MENTOR = "mentor", "Mentor"
    NETWORK_LEAD = "network_lead", "Network lead"
    NETWORK_DEPUTY_LEAD = "network_deputy_lead", "Network deputy lead"
    CIRRUS_CHAMPION = "cirrus_champion", "Cirrus champion"
    HEALTH_WELLBEING_CHAMPION = (
        "health_wellbeing_champion",
        "Health & wellbeing champion",
    )
    FAST_STREAM_REP = "fast_stream_rep", "Fast stream rep"
    OVERSEAS_STAFF_REP = "overseas_staff_rep", "Overseas staff rep"
    DIGITAL_CHAMPION = "digital_champion", "Digital champion"
    INFORMATION_MANAGER = "information_manager", "Information manager"
    INDEPENDENT_PANEL_MEMBER = "independent_panel_member", "Independent panel member"
    DIVISIONAL_SECURITY_COORDINATOR = (
        "divisional_security_coordinator",
        "Divisional security coordinator",
    )
    DDAT_CHAMPION = "ddat_champion", "DDaT champion"
    HONOURS_CHAMPION = "honours_champion", "Honours champion"


class RemoteWorking(models.TextChoices):
    OFFICE_WORKER = "office_worker", "Office worker"
    REMOTE_WORKER = "remote_worker", "Remote worker"
    SPLIT = "split", "Split"


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
    first_name = models.CharField(  # TODO: Why is this different from the PF field? when will a profile have no first name?
        max_length=200,
        null=True,
        blank=True,
    )
    preferred_first_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    last_name = models.CharField(  # TODO: Why is this different from the PF field? when will a profile have no last name?
        max_length=200,
        null=True,
        blank=True,
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
        blank=True,
        related_name="+",
    )
    contact_email = models.ForeignKey(
        "profiles.Email",
        models.SET_NULL,
        null=True,
        blank=True,
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
    edited_or_confirmed_at = models.DateTimeField(
        null=True, blank=True
    )  # TODO: This is defined in the PF codebase as `models.DateTimeField(default=timezone.now)`
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
        from profiles.services.peoplefinder import profile as peoplefinder

        self.profile_completion = peoplefinder.get_profile_completion(
            peoplefinder_profile=self
        )
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


class PeopleFinderTeamType(models.TextChoices):
    STANDARD = "standard", "Standard"
    DIRECTORATE = "directorate", "Directorate"
    PORTFOLIO = "portfolio", "Portfolio"


class PeopleFinderTeamData(TypedDict):
    slug: str
    name: str
    abbreviation: str
    children: Optional[list]
    parents: Optional[list]


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
        choices=PeopleFinderTeamType.choices,
        default=PeopleFinderTeamType.STANDARD,
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
