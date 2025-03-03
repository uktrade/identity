# This is the entrypoint service that coordinates between the sub-services
# If in doubt about what to use, you should probably be using this
import logging
from datetime import datetime
from typing import Optional

from django.db import models

from profiles.exceptions import NonCombinedProfileExists
from profiles.models import Workday
from profiles.models.combined import Profile
from profiles.models.generic import Country, UkStaffLocation
from profiles.models.peoplefinder import PeopleFinderProfile, RemoteWorking
from profiles.models.staff_sso import StaffSSOProfile
from profiles.services import combined, peoplefinder, staff_sso
from profiles.types import Unset
from user import services as user_services
from user.models import User


logger = logging.getLogger(__name__)


def get_by_id(sso_email_id: str, include_inactive: bool = False) -> Profile:
    """
    Retrieve a profile by its User ID.
    """
    return combined.get_by_id(
        sso_email_id=sso_email_id, include_inactive=include_inactive
    )


def get_by_slug(slug: str, include_inactive: bool = False) -> PeopleFinderProfile:
    """
    Retrieve a peoplefinder profile by its slug.
    """
    return peoplefinder.get_by_slug(slug=slug, include_inactive=include_inactive)


def generate_combined_profile_data(sso_email_id: str):
    """
    Figures out which info we have in specific profiles and runs through the
    field hierarchy per data type to generate the values for the combined.
    create method
    """
    sso_profile = staff_sso.get_by_id(sso_email_id=sso_email_id, include_inactive=True)

    try:
        user = sso_profile.user
    except sso_profile.DoesNotExist:
        user = user_services.get_by_id(sso_email_id=sso_email_id, include_inactive=True)

    primary_email = sso_profile.primary_email
    if primary_email is None:
        primary_email = sso_profile.emails.first().email.address
    contact_email = sso_profile.contact_email
    if contact_email is None:
        contact_email = primary_email

    return {
        "first_name": sso_profile.first_name,
        "last_name": sso_profile.last_name,
        "primary_email": primary_email,
        "contact_email": contact_email,
        "emails": sso_profile.email_addresses,
        "is_active": user.is_active,
    }


def create_from_sso(
    sso_email_id: str,
    first_name: str,
    last_name: str,
    all_emails: list[str],
    primary_email: Optional[str] = None,
    contact_email: Optional[str] = None,
) -> Profile:
    """A central function to create all relevant profile details"""
    staff_sso.create(
        sso_email_id=sso_email_id,
        first_name=first_name,
        last_name=last_name,
        all_emails=all_emails,
        primary_email=primary_email,
        contact_email=contact_email,
    )
    combined_profile_data = generate_combined_profile_data(sso_email_id=sso_email_id)

    # We might need a try/except here, if other providers (eg. oracle)
    # are going to do "create" action on the combined profile.
    return combined.create(
        sso_email_id=sso_email_id,
        first_name=combined_profile_data["first_name"],
        last_name=combined_profile_data["last_name"],
        primary_email=combined_profile_data["primary_email"],
        contact_email=combined_profile_data["contact_email"],
        all_emails=combined_profile_data["emails"],
        is_active=combined_profile_data["is_active"],
    )


def update_from_sso(
    profile: Profile,
    first_name: str,
    last_name: str,
    all_emails: list[str],
    primary_email: str | Unset | None = None,
    contact_email: str | Unset | None = None,
) -> None:
    sso_profile = staff_sso.get_by_id(
        sso_email_id=profile.sso_email_id, include_inactive=True
    )
    staff_sso.update(
        staff_sso_profile=sso_profile,
        first_name=first_name,
        last_name=last_name,
        all_emails=all_emails,
        primary_email=primary_email,
        contact_email=contact_email,
    )

    combined_profile = combined.get_by_id(
        sso_email_id=profile.sso_email_id, include_inactive=True
    )
    combined_profile_data = generate_combined_profile_data(
        sso_email_id=profile.sso_email_id
    )

    combined.update(
        profile=combined_profile,
        first_name=combined_profile_data["first_name"],
        last_name=combined_profile_data["last_name"],
        primary_email=combined_profile_data["primary_email"],
        contact_email=combined_profile_data["contact_email"],
        all_emails=combined_profile_data["emails"],
        is_active=combined_profile_data["is_active"],
    )


def create_from_peoplefinder(
    slug: str,
    user: User,
    is_active: bool,
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
    remote_working: Optional[str] = None,
    usual_office_days: Optional[str] = None,
    uk_office_location_id: Optional[str] = None,
    location_in_building: Optional[str] = None,
    international_building: Optional[str] = None,
    country_id: Optional[str] = None,
    professions: Optional[list[str]] = None,
    additional_roles: Optional[list[str]] = None,
    key_skills: Optional[list[str]] = None,
    other_key_skills: Optional[str] = None,
    learning_interests: Optional[list[str]] = None,
    other_learning_interests: Optional[str] = None,
    fluent_languages: Optional[str] = None,
    intermediate_languages: Optional[str] = None,
    previous_experience: Optional[str] = None,
) -> PeopleFinderProfile:
    return peoplefinder.create(
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

    # TODO: Update combined profile here as well


def update_from_peoplefinder(
    # TODO: update_from_peoplefinder() needs updating later
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
    # TODO: use get_by_id to get the peoplefinder_profile
    peoplefinder_profile = peoplefinder.get_by_slug(slug=slug, include_inactive=True)
    peoplefinder.update(
        peoplefinder_profile=peoplefinder_profile,
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
    # TODO: Update combined profile here as well


def delete_combined_profile(all_profiles: dict) -> None:
    # check and delete if combined profile is the only profile left for user
    if len(all_profiles) == 1 and "combined" in all_profiles:
        combined.delete_from_database(profile=all_profiles["combined"])
    else:
        raise NonCombinedProfileExists(f"All existing profiles: {all_profiles.keys()}")


def delete_sso_profile(profile: StaffSSOProfile) -> None:
    try:
        staff_sso.delete_from_database(sso_profile=profile)
    except StaffSSOProfile.DoesNotExist:
        logger.debug(
            f"Failed to delete SSO profile for {profile.sso_email_id}. SSO profile is already deleted."
        )


def delete_peoplefinder_profile(profile: PeopleFinderProfile) -> None:
    try:
        peoplefinder.delete_from_database(peoplefinder_profile=profile)
    except PeopleFinderProfile.DoesNotExist:
        logger.debug(
            f"Failed to delete People Finder profile for {profile.user.sso_email_id}. people Finder profile is already deleted."
        )


def get_all_profiles(sso_email_id: str) -> dict[str, models.Model]:
    all_profile = dict()
    try:
        all_profile["combined"] = combined.get_by_id(
            sso_email_id=sso_email_id, include_inactive=True
        )
    except:
        # no combined profile found
        pass
    try:
        all_profile["sso"] = staff_sso.get_by_id(
            sso_email_id=sso_email_id, include_inactive=True
        )
    except:
        # no sso profile found
        pass
    try:
        all_profile["peoplefinder"] = PeopleFinderProfile.objects.get(
            user__sso_email_id=sso_email_id
        )
    except:
        # no people finder profile found
        pass
    # TODO - more profiles to be added here as we implement more
    return all_profile


def archive(
    profile: Profile,
    reason: Optional[str] = None,
    requesting_user: Optional[User] = None,
) -> None:
    combined.archive(
        profile=profile,
        reason=reason,
        requesting_user=requesting_user,
    )


def unarchive(
    profile: Profile,
    reason: Optional[str] = None,
    requesting_user: Optional[User] = None,
) -> None:
    combined.unarchive(
        profile=profile,
        reason=reason,
        requesting_user=requesting_user,
    )


def delete(profile_id: str) -> dict[str, models.Model]:
    all_profiles = get_all_profiles(sso_email_id=profile_id)

    if "peoplefinder" in all_profiles:
        delete_peoplefinder_profile(profile=all_profiles["peoplefinder"])
        del all_profiles["peoplefinder"]

    if "sso" in all_profiles:
        delete_sso_profile(profile=all_profiles["sso"])
        del all_profiles["sso"]

    if "combined" in all_profiles:
        delete_combined_profile(all_profiles=all_profiles)
        del all_profiles["combined"]

    return all_profiles


def get_peoplefinder_profile_by_slug(slug: str) -> PeopleFinderProfile:
    """
    Gets peoplefinder profile from peoplefinder service
    :param slug: Peoplefinder profile slug
    """
    return peoplefinder.get_by_slug(slug=slug)


def get_countries() -> list[Country]:
    """
    Gets all countries service
    """
    return peoplefinder.get_countries()


def get_uk_staff_locations() -> list[UkStaffLocation]:
    """
    Gets all UK staff locations
    """
    return peoplefinder.get_uk_staff_locations()


def get_remote_working() -> list[tuple[RemoteWorking, str]]:
    """
    Gets all remote working options
    """
    return peoplefinder.get_remote_working()


def get_workday() -> list[tuple[Workday, str]]:
    """
    Gets all workday options
    """
    return peoplefinder.get_workday()


def get_learning_interest() -> list[tuple[Workday, str]]:
    """
    Gets all learning interest options
    """
    return peoplefinder.get_learning_interest()
