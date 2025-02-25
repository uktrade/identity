import logging
from datetime import datetime
from typing import Optional

from conftest import peoplefinder_profile
from profiles import services as profile_services
from profiles.models.combined import Profile
from profiles.models.generic import Country
from profiles.models.generic import UkStaffLocation
from profiles.models.peoplefinder import PeopleFinderProfile
from profiles.types import UNSET, Unset  # noqa
from user import services as user_services


SSO_EMAIL_ADDRESSES = "dit:emailAddress"
SSO_CONTACT_EMAIL_ADDRESS = "dit:StaffSSO:User:contactEmailAddress"
SSO_LAST_NAME = "dit:lastName"
SSO_FIRST_NAME = "dit:firstName"
SSO_USER_EMAIL_ID = "dit:StaffSSO:User:emailUserId"
SSO_USER_STATUS = "dit:StaffSSO:User:status"

logger = logging.getLogger(__name__)


def get_identity_by_id(id: str, include_inactive: bool = False) -> Profile:
    """
    Retrieve an profile by its User ID.
    """
    return profile_services.get_by_id(
        sso_email_id=id, include_inactive=include_inactive
    )


def get_profile_by_slug(
    slug: str, include_inactive: bool = False
) -> PeopleFinderProfile:
    """
    Retrieve a peoplefinder profile by its slug.
    """
    return profile_services.get_by_slug(slug=slug, include_inactive=include_inactive)


def create_peoplefinder_profile(
    slug: str,
    sso_email_id: str,
    became_inactive: Optional[datetime] = None,
    edited_or_confirmed_at: Optional[datetime] = None,
    login_count: Optional[int] = None,
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
    grade: Optional[str] = None,
    manager_slug: Optional[str] = None,
    workdays: Optional[list[str]] = None,
    remote_working: Optional[list[str]] = None,
    usual_office_days: Optional[list[str]] = None,
    uk_office_location_id: Optional[str] = None,
    location_in_building: Optional[str] = None,
    international_building: Optional[str] = None,
    country_id: Optional[str] = None,
    professions: Optional[list[str]] = None,
    additional_roles: Optional[str] = None,
    key_skills: Optional[list[str]] = None,
    other_key_skills: Optional[str] = None,
    learning_interests: Optional[list[str]] = None,
    other_learning_interests: Optional[str] = None,
    fluent_languages: Optional[str] = None,
    intermediate_languages: Optional[str] = None,
    previous_experience: Optional[str] = None,
) -> PeopleFinderProfile:
    """
    Entrypoint for peoplefinder profile creation. Triggers the creation of Peoplefinder record.
    """
    user = user_services.get_by_id(sso_email_id=sso_email_id)
    return profile_services.create_from_peoplefinder(
        slug=slug,
        user=user,
        is_active=user.is_active,
        became_inactive=became_inactive,
        edited_or_confirmed_at=edited_or_confirmed_at,
        login_count=login_count,
        first_name=first_name,
        preferred_first_name=preferred_first_name,
        last_name=last_name,
        pronouns=pronouns,
        name_pronunciation=name_pronunciation,
        email_address=email_address,
        contact_email_address=contact_email_address,
        primary_phone_number=primary_phone_number,
        secondary_phone_number=secondary_phone_number,
        photo=photo,
        photo_small=photo_small,
        grade=grade,
        manager_slug=manager_slug,
        workdays=workdays,
        remote_working=remote_working,
        usual_office_days=usual_office_days,
        uk_office_location_id=uk_office_location_id,
        location_in_building=location_in_building,
        international_building=international_building,
        country_id=country_id,
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


def update_peoplefinder_profile(
    profile: Profile,
    slug: str,
    is_active: bool,
    became_inactive: Optional[datetime] = None,
    edited_or_confirmed_at: Optional[datetime] = None,
    login_count: Optional[int] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    preferred_first_name: Optional[str | Unset] = None,
    pronouns: Optional[str | Unset] = None,
    name_pronunciation: Optional[str | Unset] = None,
    email_address: Optional[str | Unset] = None,
    contact_email_address: Optional[str | Unset] = None,
    primary_phone_number: Optional[str | Unset] = None,
    secondary_phone_number: Optional[str | Unset] = None,
    photo: Optional[str | Unset] = None,
    photo_small: Optional[str | Unset] = None,
    grade: Optional[str | Unset] = None,
    manager_slug: Optional[str | Unset] = None,
    not_employee: Optional[bool | Unset] = None,
    workdays: Optional[list[str] | Unset] = None,
    remote_working: Optional[str | Unset] = None,
    usual_office_days: Optional[str | Unset] = None,
    uk_office_location_id: Optional[str | Unset] = None,
    location_in_building: Optional[str | Unset] = None,
    international_building: Optional[str | Unset] = None,
    country_id: Optional[str] = None,
    professions: Optional[list[str] | Unset] = None,
    additional_roles: Optional[list[str] | Unset] = None,
    other_additional_roles: Optional[str | Unset] = None,
    key_skills: Optional[list[str] | Unset] = None,
    other_key_skills: Optional[str | Unset] = None,
    learning_interests: Optional[list[str] | Unset] = None,
    other_learning_interests: Optional[str | Unset] = None,
    fluent_languages: Optional[str | Unset] = None,
    intermediate_languages: Optional[str | Unset] = None,
    previous_experience: Optional[str | Unset] = None,
) -> None:
    """
    Entrypoint for peoplefinder profile creation. Triggers the creation of Peoplefinder record.
    """
    profile_services.update_from_peoplefinder(
        profile=profile,
        slug=slug,
        is_active=is_active,
        became_inactive=became_inactive,
        edited_or_confirmed_at=edited_or_confirmed_at,
        login_count=login_count,
        first_name=first_name,
        last_name=last_name,
        preferred_first_name=preferred_first_name,
        pronouns=pronouns,
        name_pronunciation=name_pronunciation,
        email_address=email_address,
        contact_email_address=contact_email_address,
        primary_phone_number=primary_phone_number,
        secondary_phone_number=secondary_phone_number,
        photo=photo,
        photo_small=photo_small,
        grade=grade,
        manager_slug=manager_slug,
        not_employee=not_employee,
        workdays=workdays,
        remote_working=remote_working,
        usual_office_days=usual_office_days,
        uk_office_location_id=uk_office_location_id,
        location_in_building=location_in_building,
        international_building=international_building,
        country_id=country_id,
        professions=professions,
        additional_roles=additional_roles,
        other_additional_roles=other_additional_roles,
        key_skills=key_skills,
        other_key_skills=other_key_skills,
        learning_interests=learning_interests,
        other_learning_interests=other_learning_interests,
        fluent_languages=fluent_languages,
        intermediate_languages=intermediate_languages,
        previous_experience=previous_experience,
    )


def create_identity(
    id: str,
    first_name: str,
    last_name: str,
    all_emails: list[str],
    is_active: bool,
    primary_email: str | Unset | None = None,
    contact_email: str | Unset | None = None,
) -> Profile:
    """
    Entrypoint for new user creation. Triggers the creation of User record,
    then the relevant Profile record as well as a combined Profile.

    Returns the combined Profile
    """
    user_services.create(
        sso_email_id=id,
        is_active=is_active,
    )
    return profile_services.create_from_sso(
        sso_email_id=id,
        first_name=first_name,
        last_name=last_name,
        all_emails=all_emails,
        contact_email=contact_email,
        primary_email=primary_email,
    )


def update_identity(
    profile: Profile,
    first_name: str,
    last_name: str,
    all_emails: list[str],
    is_active: bool,
    primary_email: str | Unset | None = None,
    contact_email: str | Unset | None = None,
) -> None:
    """
    Function for updating an existing user (archive / unarchive) and their profile information.
    """

    user = user_services.get_by_id(
        sso_email_id=profile.sso_email_id, include_inactive=True
    )
    if user.is_active != is_active:
        if user.is_active == False:
            user_services.unarchive(user)
            profile_services.unarchive(profile=profile)
        else:
            user_services.archive(user)
            profile_services.archive(profile=profile)

    profile_services.update_from_sso(
        profile=profile,
        first_name=first_name,
        last_name=last_name,
        all_emails=all_emails,
        primary_email=primary_email,
        contact_email=contact_email,
    )


def delete_identity(profile: Profile) -> None:
    """
    Function for deleting an existing user and their profile information.
    """
    profile_id = profile.sso_email_id

    all_remaining_profiles = profile_services.delete(profile_id=profile_id)

    # delete user if no profile exists for user
    if not all_remaining_profiles:
        user = user_services.get_by_id(sso_email_id=profile_id, include_inactive=True)
        user_services.delete_from_database(user=user)


def get_peoplefinder_profile_by_slug(slug: str) -> PeopleFinderProfile:
    """
    Retrieve peoplefinder profile by its slug.
    """
    return profile_services.get_peoplefinder_profile_by_slug(slug=slug)


def get_countries() -> list[Country]:
    """
    Function for getting a list of all countries
    """
    return profile_services.get_countries()
  
def get_uk_staff_locations() -> list[UkStaffLocation]:
    return profile_services.get_uk_staff_locations()
