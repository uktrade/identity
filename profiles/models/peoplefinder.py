import uuid
from typing import Iterator, Optional

from django.db import models
from django.db.models import F, Q
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import escape, strip_tags
from django.utils.safestring import mark_safe

from django_chunk_upload_handlers.clam_av import validate_virus_check_result

from profiles.models.abstract import AbstractHistoricalModel


# United Kingdom
DEFAULT_COUNTRY_PK = "CTHMTC00260"


class LearningInterest(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["code"], name="unique_learning_interest_code"
            ),
            models.UniqueConstraint(
                fields=["name"], name="unique_learning_interest_name"
            ),
        ]
        ordering = ["name"]

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name


class AdditionalRole(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["code"], name="unique_additional_role_code"
            ),
            models.UniqueConstraint(
                fields=["name"], name="unique_additional_role_name"
            ),
        ]
        ordering = ["name"]

    code = models.CharField(max_length=40)
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name


def person_photo_path(instance, filename):
    return f"peoplefinder/person/{instance.slug}/photo/{filename}"


def person_photo_small_path(instance, filename):
    return f"peoplefinder/person/{instance.slug}/photo/small_{filename}"


class PeopleFinderProfile(AbstractHistoricalModel):
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~Q(id=F("manager")), name="manager_cannot_be_self"
            ),
        ]
        indexes = [
            models.Index(fields=['slug']),
        ]

    class RemoteWorking(models.TextChoices):
        OFFICE_WORKER = (
            "office_worker",
            "I work primarily from the office",
        )
        REMOTE_WORKER = (
            "remote_worker",
            "I work primarily from home (remote worker)",
        )
        SPLIT = (
            "split",
            "I split my time between home and the office",
        )

    slug = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.OneToOneField(
        "user.User", models.CASCADE, null=True, blank=True, related_name="profile"
    )

    # Basic Profile info
    #
    first_name = models.CharField(
        max_length=200,
        help_text=(
            "If you enter a preferred name below, this name will be hidden to others"
        ),
    )
    preferred_first_name = models.CharField(
        max_length=200,
        help_text=(
            "This name appears on your profile. Colleagues can search for you"
            " using either of your first names"
        ),
        null=True,
        blank=True,
    )
    last_name = models.CharField(
        max_length=200,
    )
    pronouns = models.CharField(max_length=40, null=True, blank=True)
    name_pronunciation = models.CharField(
        "How to pronounce your full name",
        help_text=mark_safe(  # noqa: S308
            "A phonetic representation of your name<br><a class='govuk-link' href='/news-and-views/say-my-name/' target='_blank' rel='noreferrer'>"
            "Tips for writing your name phonetically</a>"
        ),
        max_length=200,
        null=True,
        blank=True,
    )
    email = models.EmailField(
        "How we contact you",
        help_text="We will send Digital Workspace notifications to this email",
    )
    contact_email = models.EmailField(
        "Email address",
        null=True,
        blank=True,
        help_text="The work email you want people to contact you on",
    )
    primary_phone_number = models.CharField(
        "Phone number",
        max_length=42,
        null=True,
        blank=True,
        help_text=(
            "Enter the country's dialling code in place of the first 0. The"
            " UK's dialling code is +44."
        ),
    )
    secondary_phone_number = models.CharField(
        "Alternative phone number",
        max_length=160,
        null=True,
        blank=True,
        help_text=(
            "Enter the country's dialling code in place of the first 0. The"
            " UK's dialling code is +44."
        ),
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
    grade = models.ForeignKey(
        "Grade", models.SET_NULL, null=True, blank=True, related_name="+"
    )
    manager = models.ForeignKey(
        "PeopleFinderProfile", models.SET_NULL, null=True, blank=True, related_name="direct_reports"
    )
    do_not_work_for_dit = models.BooleanField(
        "My manager is not listed because I do not work for DBT", default=False
    )

    # Working patterns
    #
    workdays = models.ManyToManyField(
        "Workday",
        verbose_name="Which days do you usually work?",
        blank=True,
        related_name="+",
    )
    remote_working = models.CharField(
        verbose_name="Where do you usually work?",
        blank=True,
        null=True,
        max_length=80,
        choices=RemoteWorking.choices,
    )
    usual_office_days = models.CharField(
        "What days do you usually come in to the office?",
        help_text=("For example: I usually come in on Mondays and Wednesdays"),
        max_length=200,
        null=True,
        blank=True,
    )
    uk_office_location = models.ForeignKey(
        "UkStaffLocation",
        verbose_name="What is your office location?",
        help_text="Your base location as per your contract",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    location_in_building = models.CharField(
        "Location in the building",
        max_length=130,
        null=True,
        blank=True,
        help_text="If you sit in a particular area, you can let colleagues know here",
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
        default=DEFAULT_COUNTRY_PK, #  type: ignore
        related_name="+",
    )

    # Supplementary info
    #
    professions = models.ManyToManyField(
        "Profession",
        verbose_name="What professions do you belong to?",
        blank=True,
        related_name="+",
        help_text="Select all that apply",
    )
    additional_roles = models.ManyToManyField(
        "AdditionalRole",
        verbose_name="Do you have any additional roles or responsibilities?",
        blank=True,
        related_name="+",
        help_text="Select all that apply",
    )
    other_additional_roles = models.CharField(
        "What other additional roles or responsibilities do you have?",
        max_length=400,
        null=True,
        blank=True,
        help_text="Enter your roles or responsibilities. Use a comma to separate them.",
    )
    key_skills = models.ManyToManyField(
        "KeySkill",
        verbose_name="What are your skills?",
        blank=True,
        related_name="+",
        help_text="Select all that apply",
    )
    other_key_skills = models.CharField(
        "What other skills do you have?",
        max_length=700,
        null=True,
        blank=True,
        help_text="Enter your skills. Use a comma to separate them.",
    )
    learning_interests = models.ManyToManyField(
        "LearningInterest",
        verbose_name="What are your learning and development interests?",
        blank=True,
        related_name="+",
        help_text="Select all that apply",
    )
    other_learning_interests = models.CharField(
        "What other learning and development interests do you have?",
        max_length=255,
        null=True,
        blank=True,
        help_text="Enter your interests. Use a comma to separate them.",
    )
    fluent_languages = models.CharField(
        "Which languages are you fluent in?",
        max_length=200,
        null=True,
        blank=True,
        help_text="Use a comma to separate the languages. For example: French, Polish, Ukrainian",
    )
    intermediate_languages = models.CharField(
        "Which other languages do you speak?",
        max_length=200,
        null=True,
        blank=True,
        help_text="These are languages you speak and write but are not fluent in",
    )
    previous_experience = models.TextField(
        "Previous positions I have held",
        null=True,
        blank=True,
        help_text="List where you have worked before your current role",
    )

    # Metadata and status
    #
    is_active = models.BooleanField(default=True)
    became_inactive = models.DateTimeField(null=True, blank=True)
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

    @property
    def full_name(self) -> str:
        first_name = self.get_first_name_display()
        return f"{first_name} {self.last_name}"

    @property
    def is_line_manager(self) -> bool:
        return self.direct_reports.exists()  # type: ignore

    @property
    def all_languages(self) -> str:
        return ", ".join(
            filter(None, [self.fluent_languages, self.intermediate_languages])
        )

    @property
    def has_photo(self) -> bool:
        return bool(self.photo)

    # def save(self, *args, **kwargs):
    #     from peoplefinder.services.person import PersonService

    #     self.profile_completion = PersonService().get_profile_completion(person=self)
    #     return super().save(*args, **kwargs)

    def get_first_name_display(self) -> str:
        if self.preferred_first_name:
            return self.preferred_first_name
        return self.first_name

    def get_workdays_display(self) -> str:
        workdays = self.workdays.all_mon_to_sun()  # type: ignore

        workday_codes = [x.code for x in workdays]
        mon_to_fri_codes = ["mon", "tue", "wed", "thu", "fri"]

        # "Monday to Friday"
        if workday_codes == mon_to_fri_codes:
            return f"{workdays[0]} to {workdays[-1]}"

        # "Monday, Tuesday, Wednesday, ..."
        return ", ".join(map(str, workdays))

    def get_office_location_display(self) -> str:
        if self.international_building:
            return self.international_building

        location_parts = []

        if self.location_in_building:
            location_parts.append(escape(strip_tags(self.location_in_building)))

        if self.uk_office_location:
            location_parts.append(self.uk_office_location.building_name)
            location_parts.append(self.uk_office_location.city)

        return mark_safe("<br>".join(location_parts))  # noqa: S308

    # def get_manager_display(self) -> Optional[str]:
    #     if self.manager:
    #         return mark_safe(  # noqa: S308
    #             render_to_string(
    #                 "peoplefinder/components/profile-link.html",
    #                 {
    #                     "profile": self.manager,
    #                     "data_testid": "manager",
    #                 },
    #             )
    #         )
    #     return None

    # def get_roles_display(self) -> Optional[str]:
    #     output = ""
    #     for role in self.roles.select_related("team").all():
    #         output += render_to_string(
    #             "peoplefinder/components/profile-role.html", {"role": role}
    #         )
    #     return mark_safe(output)  # noqa: S308

    def get_grade_display(self) -> Optional[str]:
        if self.grade:
            return self.grade.name
        return None

    def get_all_key_skills(self) -> Iterator[str]:
        yield from self.key_skills.all()

        if self.other_key_skills:
            yield self.other_key_skills

    def get_key_skills_display(self) -> Optional[str]:
        if self.key_skills.exists() or self.other_key_skills:
            skills_list = []
            skills_list += self.key_skills.values_list("name", flat=True)
            if self.other_key_skills:
                skills_list.append(self.other_key_skills)
            return ", ".join(skills_list)

        return None

    def get_all_learning_interests(self) -> Iterator[str]:
        yield from self.learning_interests.all()

        if self.other_learning_interests:
            yield self.other_learning_interests

    def get_learning_interests_display(self) -> Optional[str]:
        if self.learning_interests.exists() or self.other_learning_interests:
            interests_list = []
            interests_list += self.learning_interests.values_list("name", flat=True)
            if self.other_learning_interests:
                interests_list.append(self.other_learning_interests)
            return ", ".join(interests_list)

        return None

    def get_professions_display(self) -> Optional[str]:
        if self.professions.exists():
            return ", ".join(self.professions.values_list("name", flat=True))

        return None

    def get_all_additional_roles(self) -> Iterator[str]:
        yield from self.additional_roles.all()

        if self.other_additional_roles:
            yield self.other_additional_roles

    def get_additional_roles_display(self) -> Optional[str]:
        if self.additional_roles.exists() or self.other_additional_roles:
            additional_roles_list = []
            additional_roles_list += self.additional_roles.values_list(
                "name", flat=True
            )
            if self.other_additional_roles:
                additional_roles_list.append(self.other_additional_roles)
            return ", ".join(additional_roles_list)

        return None


class PeopleFinderProfileTeam(AbstractHistoricalModel):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["peoplefinder_profile", "team", "job_title", "head_of_team"],
                name="unique_team_member",
            ),
        ]

    peoplefinder_profile = models.ForeignKey("PeopleFinderProfile", models.CASCADE, related_name="roles")
    team = models.ForeignKey("Team", models.CASCADE, related_name="peoplefinder_members")

    job_title = models.CharField(
        max_length=255, help_text="Enter your role in this team"
    )
    head_of_team = models.BooleanField(default=False)
    leaders_position = models.SmallIntegerField(null=True)

    def __str__(self) -> str:
        return f"{self.team} - {self.peoplefinder_profile}"


class PeopleFinderTeamTree(AbstractHistoricalModel):
    class Meta:
        unique_together = [["parent", "child"]]

    parent = models.ForeignKey("Team", models.CASCADE, related_name="parents")
    child = models.ForeignKey("Team", models.CASCADE, related_name="children")

    depth = models.SmallIntegerField()

    def __str__(self) -> str:
        return f"{self.parent} - {self.child} ({self.depth})"
