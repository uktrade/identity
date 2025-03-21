from datetime import datetime
from typing import TYPE_CHECKING, Optional

from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.auth import get_user_model

from profiles.exceptions import ProfileExists
from profiles.models import LearningInterest, Workday
from profiles.models.generic import Country, Email, Grade, Profession, UkStaffLocation
from profiles.models.peoplefinder import (
    AdditionalRole,
    KeySkill,
    PeopleFinderProfile,
    RemoteWorking,
)
from profiles.types import UNSET, Unset


if TYPE_CHECKING:
    from user.models import User
else:
    User = get_user_model()


def get_profile_completion(peoplefinder_profile):
    # TODO: Implement get_profile_completion() function.
    return 0


def get_by_slug(slug: str, include_inactive: bool = False) -> PeopleFinderProfile:
    """
    Retrieve a People Finder profile by its Slug.
    """
    if include_inactive:
        return PeopleFinderProfile.objects.get(slug=slug)

    return PeopleFinderProfile.objects.get(slug=slug, is_active=True)


def create(
    slug: str,
    user: User,
    is_active: bool,
    became_inactive: Optional[datetime] = None,
    edited_or_confirmed_at: Optional[datetime] = None,
    login_count: int = 0,
    first_name: Optional[str] = None,
    preferred_first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    pronouns: Optional[str] = None,
    name_pronunciation: Optional[str] = None,
    email_address: Optional[str] = None,
    contact_email_address: Optional[str] = None,
    primary_phone_number: Optional[str] = None,
    secondary_phone_number: Optional[str] = None,
    photo: Optional[str] = None,
    photo_small: Optional[str] = None,
    grade: Optional[Grade] = None,
    manager_slug: Optional[str] = None,
    not_employee: bool = False,
    workdays: Optional[list[Workday]] = None,
    remote_working: Optional[RemoteWorking] = None,
    usual_office_days: Optional[str] = None,
    uk_office_location_id: Optional[str] = None,
    location_in_building: Optional[str] = None,
    international_building: Optional[str] = None,
    country_id: str = "CTHMTC00260",
    professions: Optional[list[Profession]] = None,
    additional_roles: Optional[list[AdditionalRole]] = None,
    key_skills: Optional[list[KeySkill]] = None,
    other_key_skills: Optional[str] = None,
    learning_interests: Optional[list[LearningInterest]] = None,
    other_learning_interests: Optional[str] = None,
    fluent_languages: Optional[str] = None,
    intermediate_languages: Optional[str] = None,
    previous_experience: Optional[str] = None,
) -> PeopleFinderProfile:
    try:
        PeopleFinderProfile.objects.get(slug=slug)
        raise ProfileExists("Profile has been previously created")
    except PeopleFinderProfile.DoesNotExist:
        peoplefinder_profile = PeopleFinderProfile(
            slug=slug,
            user=user,
            is_active=is_active,
            became_inactive=became_inactive,
            edited_or_confirmed_at=edited_or_confirmed_at,
            login_count=login_count,
            first_name=first_name,
            preferred_first_name=preferred_first_name,
            last_name=last_name,
            pronouns=pronouns,
            name_pronunciation=name_pronunciation,
            email=set_email_details(address=email_address),
            contact_email=set_email_details(address=contact_email_address),
            primary_phone_number=primary_phone_number,
            secondary_phone_number=secondary_phone_number,
            photo=photo,
            photo_small=photo_small,
            grade=grade,
            manager=set_manager(manager_slug=manager_slug),
            not_employee=not_employee,
            workdays=workdays,
            remote_working=remote_working,
            usual_office_days=usual_office_days,
            uk_office_location=set_uk_office_location(
                uk_office_location_id=uk_office_location_id
            ),
            location_in_building=location_in_building,
            international_building=international_building,
            country=set_country(country_id=country_id),
            professions=professions,
            additional_roles=additional_roles,
            key_skills=key_skills,
            other_key_skills=other_key_skills,
            learning_interests=learning_interests,
            other_learning_interests=other_learning_interests,
            fluent_languages=fluent_languages,
            intermediate_languages=intermediate_languages,
            previous_experience=previous_experience,
        )
        peoplefinder_profile.full_clean()
        peoplefinder_profile.save()
        return peoplefinder_profile


def update(
    peoplefinder_profile: PeopleFinderProfile,
    is_active: Optional[bool] = None,
    became_inactive: Optional[datetime | Unset] = None,
    edited_or_confirmed_at: Optional[datetime | Unset] = None,
    login_count: Optional[int] = None,
    first_name: Optional[str | Unset] = None,
    last_name: Optional[str | Unset] = None,
    preferred_first_name: Optional[str | Unset] = None,
    pronouns: Optional[str | Unset] = None,
    name_pronunciation: Optional[str | Unset] = None,
    email_address: Optional[str | Unset] = None,
    contact_email_address: Optional[str | Unset] = None,
    primary_phone_number: Optional[str | Unset] = None,
    secondary_phone_number: Optional[str | Unset] = None,
    photo: Optional[str | Unset] = None,
    photo_small: Optional[str | Unset] = None,
    grade: Optional[Grade | Unset] = None,
    manager_slug: Optional[str | Unset] = None,
    not_employee: Optional[bool] = None,
    workdays: Optional[list[Workday] | Unset] = None,
    remote_working: Optional[RemoteWorking | Unset] = None,
    usual_office_days: Optional[str | Unset] = None,
    uk_office_location_id: Optional[str | Unset] = None,
    location_in_building: Optional[str | Unset] = None,
    international_building: Optional[str | Unset] = None,
    country_id: Optional[str] = None,
    professions: Optional[list[Profession] | Unset] = None,
    additional_roles: Optional[list[AdditionalRole] | Unset] = None,
    other_additional_roles: Optional[str | Unset] = None,
    key_skills: Optional[list[KeySkill] | Unset] = None,
    other_key_skills: Optional[str | Unset] = None,
    learning_interests: Optional[list[LearningInterest] | Unset] = None,
    other_learning_interests: Optional[str | Unset] = None,
    fluent_languages: Optional[str | Unset] = None,
    intermediate_languages: Optional[str | Unset] = None,
    previous_experience: Optional[str | Unset] = None,
) -> None:

    update_fields: list = []

    # Update fields that are required on the PeopleFinderProfile
    if is_active:
        peoplefinder_profile.is_active = is_active
        update_fields.append("is_active")
    if login_count:
        peoplefinder_profile.login_count = login_count
        update_fields.append("login_count")
    if not_employee:
        peoplefinder_profile.not_employee = not_employee
        update_fields.append("not_employee")
    if country_id:
        peoplefinder_profile.country = set_country(country_id=country_id)
        update_fields.append("country")

    # Update fields that are optional on the PeopleFinderProfile
    if became_inactive is not None:
        if became_inactive is UNSET:
            peoplefinder_profile.became_inactive = None
        else:
            peoplefinder_profile.became_inactive = became_inactive
        update_fields.append("became_inactive")
    if edited_or_confirmed_at is not None:
        if edited_or_confirmed_at is UNSET:
            peoplefinder_profile.edited_or_confirmed_at = None
        else:
            peoplefinder_profile.edited_or_confirmed_at = edited_or_confirmed_at
        update_fields.append("edited_or_confirmed_at")

    if first_name is not None:
        if first_name is UNSET:
            peoplefinder_profile.first_name = None
        else:
            peoplefinder_profile.first_name = first_name
        update_fields.append("first_name")
    if last_name is not None:
        if last_name is UNSET:
            peoplefinder_profile.last_name = None
        else:
            peoplefinder_profile.last_name = last_name
        update_fields.append("last_name")
    if preferred_first_name is not None:
        if preferred_first_name is UNSET:
            peoplefinder_profile.preferred_first_name = None
        else:
            peoplefinder_profile.preferred_first_name = preferred_first_name
        update_fields.append("preferred_first_name")
    if pronouns is not None:
        if pronouns is UNSET:
            peoplefinder_profile.pronouns = None
        else:
            peoplefinder_profile.pronouns = pronouns
        update_fields.append("pronouns")
    if pronouns is not None:
        if pronouns is UNSET:
            peoplefinder_profile.pronouns = None
        else:
            peoplefinder_profile.pronouns = pronouns
        update_fields.append("pronouns")
    if name_pronunciation is not None:
        if name_pronunciation is UNSET:
            peoplefinder_profile.name_pronunciation = None
        else:
            peoplefinder_profile.name_pronunciation = name_pronunciation
        update_fields.append("name_pronunciation")
    if email_address is not None:
        if email_address is UNSET:
            peoplefinder_profile.email = None
        else:
            peoplefinder_profile.email = set_email_details(address=email_address)
        update_fields.append("email")
    if contact_email_address is not None:
        if contact_email_address is UNSET:
            peoplefinder_profile.contact_email = None
        else:
            peoplefinder_profile.contact_email = set_email_details(
                address=contact_email_address
            )
        update_fields.append("contact_email")
    if primary_phone_number is not None:
        if primary_phone_number is UNSET:
            peoplefinder_profile.primary_phone_number = None
        else:
            peoplefinder_profile.primary_phone_number = primary_phone_number
        update_fields.append("primary_phone_number")
    if secondary_phone_number is not None:
        if secondary_phone_number is UNSET:
            peoplefinder_profile.secondary_phone_number = None
        else:
            peoplefinder_profile.secondary_phone_number = secondary_phone_number
        update_fields.append("secondary_phone_number")
    if photo is not None:
        if photo is UNSET:
            peoplefinder_profile.photo = None
        else:
            peoplefinder_profile.photo = photo
        update_fields.append("photo")
    if photo_small is not None:
        if photo_small is UNSET:
            peoplefinder_profile.photo_small = None
        else:
            peoplefinder_profile.photo_small = photo_small
        update_fields.append("photo_small")
    if grade is not None:
        if grade is UNSET:
            peoplefinder_profile.grade = None
        else:
            peoplefinder_profile.grade = grade
        update_fields.append("grade")
    if manager_slug is not None:
        if manager_slug is UNSET:
            peoplefinder_profile.manager = None
        else:
            peoplefinder_profile.manager = set_manager(manager_slug=manager_slug)
        update_fields.append("manager")
    if workdays is not None:
        if workdays is UNSET:
            # TODO: Discuss the type ignore below, something about the
            # `ChoiceArrayField` class is causing us issues.
            # Why aren't we just doing https://stackoverflow.com/a/38934721? - Cam
            peoplefinder_profile.workdays = []  # type: ignore
        else:
            peoplefinder_profile.workdays = workdays  # type: ignore
        update_fields.append("workdays")
    if remote_working is not None:
        if remote_working is UNSET:
            peoplefinder_profile.remote_working = None
        else:
            peoplefinder_profile.remote_working = remote_working
        update_fields.append("remote_working")
    if usual_office_days is not None:
        if usual_office_days is UNSET:
            peoplefinder_profile.usual_office_days = None
        else:
            peoplefinder_profile.usual_office_days = usual_office_days
        update_fields.append("usual_office_days")
    if uk_office_location_id is not None:
        if uk_office_location_id is UNSET:
            peoplefinder_profile.uk_office_location = None
        else:
            peoplefinder_profile.uk_office_location = set_uk_office_location(
                uk_office_location_id=uk_office_location_id
            )
        update_fields.append("uk_office_location")
    if location_in_building is not None:
        if location_in_building is UNSET:
            peoplefinder_profile.location_in_building = None
        else:
            peoplefinder_profile.location_in_building = location_in_building
        update_fields.append("location_in_building")
    if international_building is not None:
        if international_building is UNSET:
            peoplefinder_profile.international_building = None
        else:
            peoplefinder_profile.international_building = international_building
        update_fields.append("international_building")
    if professions is not None:
        if professions is UNSET:
            peoplefinder_profile.professions = None  # type: ignore
        else:
            peoplefinder_profile.professions = professions  # type: ignore
        update_fields.append("professions")
    if additional_roles is not None:
        if additional_roles is UNSET:
            peoplefinder_profile.additional_roles = None  # type: ignore
        else:
            peoplefinder_profile.additional_roles = additional_roles  # type: ignore
        update_fields.append("additional_roles")
    if other_additional_roles is not None:
        if other_additional_roles is UNSET:
            peoplefinder_profile.other_additional_roles = None
        else:
            peoplefinder_profile.other_additional_roles = other_additional_roles
        update_fields.append("other_additional_roles")
    if key_skills is not None:
        if key_skills is UNSET:
            peoplefinder_profile.key_skills = None  # type: ignore
        else:
            peoplefinder_profile.key_skills = key_skills  # type: ignore
        update_fields.append("key_skills")
    if other_key_skills is not None:
        if other_key_skills is UNSET:
            peoplefinder_profile.other_key_skills = None
        else:
            peoplefinder_profile.other_key_skills = other_key_skills
        update_fields.append("other_key_skills")
    if learning_interests is not None:
        if learning_interests is UNSET:
            peoplefinder_profile.learning_interests = None  # type: ignore
        else:
            peoplefinder_profile.learning_interests = learning_interests  # type: ignore
        update_fields.append("learning_interests")
    if other_learning_interests is not None:
        if other_learning_interests is UNSET:
            peoplefinder_profile.other_learning_interests = None
        else:
            peoplefinder_profile.other_learning_interests = other_learning_interests
        update_fields.append("other_learning_interests")
    if fluent_languages is not None:
        if fluent_languages is UNSET:
            peoplefinder_profile.fluent_languages = None
        else:
            peoplefinder_profile.fluent_languages = fluent_languages
        update_fields.append("fluent_languages")
    if intermediate_languages is not None:
        if intermediate_languages is UNSET:
            peoplefinder_profile.intermediate_languages = None
        else:
            peoplefinder_profile.intermediate_languages = intermediate_languages
        update_fields.append("intermediate_languages")
    if previous_experience is not None:
        if previous_experience is UNSET:
            peoplefinder_profile.previous_experience = None
        else:
            peoplefinder_profile.previous_experience = previous_experience
        update_fields.append("previous_experience")

    # Save the changes to the PeopleFinderProfile
    peoplefinder_profile.full_clean()
    peoplefinder_profile.save(update_fields=update_fields)


def delete_from_database(
    peoplefinder_profile: PeopleFinderProfile,
    reason: Optional[str] = None,
    requesting_user: Optional[User] = None,
) -> None:
    """Really delete a People Finder Profile"""
    if reason is None:
        reason = "Deleting People Finder Profile record"
    requesting_user_id = "via-api"
    if requesting_user is not None:
        requesting_user_id = requesting_user.pk
    LogEntry.objects.log_action(
        user_id=requesting_user_id,
        content_type_id=get_content_type_for_model(peoplefinder_profile).pk,
        object_id=peoplefinder_profile.pk,
        object_repr=str(peoplefinder_profile),
        change_message=reason,
        action_flag=DELETION,
    )

    peoplefinder_profile.delete()


###############################################################
# Email data methods
###############################################################
def set_email_details(address: str | None) -> Optional[Email]:
    if address is not None and len(address.strip()) > 0:
        email, _ = Email.objects.get_or_create(address=address)
        return email
    return None


def set_manager(manager_slug: str | None) -> Optional[PeopleFinderProfile]:
    if manager_slug is not None:
        return PeopleFinderProfile.objects.get(slug=manager_slug)
    return None


def set_uk_office_location(
    uk_office_location_id: str | None,
) -> Optional[UkStaffLocation]:
    if uk_office_location_id is not None:
        return UkStaffLocation.objects.get(code=uk_office_location_id)
    return None


def set_country(country_id: str | None) -> Optional[Country]:
    if country_id is not None:
        return Country.objects.get(reference_id=country_id)
    return None


def get_countries() -> list[Country]:
    """
    Gets all countries service
    """
    return list(Country.objects.all())


def get_uk_staff_locations() -> list[UkStaffLocation]:
    """
    Gets all UK staff locations
    """
    return list(UkStaffLocation.objects.all())


def get_remote_working() -> list[tuple[RemoteWorking, str]]:
    """
    Gets all remote working options
    """
    return RemoteWorking.choices


def get_workdays() -> list[tuple[Workday, str]]:
    """
    Gets all workdays
    """
    return Workday.choices


def get_learning_interests() -> list[tuple[LearningInterest, str]]:
    """
    Gets all learning interests
    """
    return LearningInterest.choices


def get_professions() -> list[tuple[Profession, str]]:
    """
    Gets all professions
    """
    return Profession.choices


def get_grades() -> list[tuple[Grade, str]]:
    """
    Gets all grades
    """
    return Grade.choices


def get_key_skills() -> list[tuple[KeySkill, str]]:
    """
    Gets all key skills
    """
    return KeySkill.choices


def get_additional_roles() -> list[tuple[AdditionalRole, str]]:
    """
    Get all additional roles
    """
    return AdditionalRole.choices
