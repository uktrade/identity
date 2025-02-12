# This is the entrypoint service that coordinates between the sub-services
# If in doubt about what to use, you should probably be using this
from typing import Optional

from django.contrib.admin.models import DELETION, LogEntry
from django.db import models

from profiles.models.combined import Profile
from profiles.models.generic import Country, UkStaffLocation
from profiles.models.peoplefinder import PeopleFinderProfile
from profiles.services import combined, peoplefinder, staff_sso
from profiles.types import Unset
from user.models import User


def get_by_id(sso_email_id: str, include_inactive: bool = False) -> Profile:
    """
    Retrieve a profile by its User ID.
    """
    return combined.get_by_id(
        sso_email_id=sso_email_id, include_inactive=include_inactive
    )


def generate_combined_profile_data(sso_email_id: str):
    """
    Figures out which info we have in specific profiles and runs through the
    field hierarchy per data type to generate the values for the combined.
    create method
    """
    sso_profile = staff_sso.get_by_id(sso_email_id=sso_email_id, include_inactive=True)
    user = sso_profile.user

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


# TODO: update_from_peoplefinder() needs updating later
def update_from_peoplefinder(
    profile: Profile,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    preferred_first_name: Optional[str | Unset] = None,
    pronouns: Optional[str | Unset] = None,
    name_pronunciation: Optional[str | Unset] = None,
    email: Optional[str | Unset] = None,
    contact_email: Optional[str | Unset] = None,
    primary_phone_number: Optional[str | Unset] = None,
    secondary_phone_number: Optional[str | Unset] = None,
    photo: Optional[str | Unset] = None,
    photo_small: Optional[str | Unset] = None,
    grade: Optional[str | Unset] = None,
    manager: Optional[PeopleFinderProfile | Unset] = None,
    not_employee: Optional[bool | Unset] = None,
    workdays: Optional[list[str] | Unset] = None,
    remote_working: Optional[str | Unset] = None,
    usual_office_days: Optional[str | Unset] = None,
    uk_office_location: Optional[UkStaffLocation | Unset] = None,
    location_in_building: Optional[str | Unset] = None,
    international_building: Optional[str | Unset] = None,
    country: Optional[Country] = None,
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
    user = User.objects.get(sso_email_id=profile.sso_email_id)
    peoplefinder_profile = PeopleFinderProfile.objects.get(user=user)
    peoplefinder.update(
        peoplefinder_profile=peoplefinder_profile,
        first_name=first_name,
        last_name=last_name,
        preferred_first_name=preferred_first_name,
        pronouns=pronouns,
        name_pronunciation=name_pronunciation,
        email=email,
        contact_email=contact_email,
        primary_phone_number=primary_phone_number,
        secondary_phone_number=secondary_phone_number,
        photo=photo,
        photo_small=photo_small,
        grade=grade,
        manager=manager,
        not_employee=not_employee,
        workdays=workdays,
        remote_working=remote_working,
        usual_office_days=usual_office_days,
        uk_office_location=uk_office_location,
        location_in_building=location_in_building,
        international_building=international_building,
        country=country,
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


def delete_from_peoplefinder(profile: Profile) -> None:
    try:
        peoplefinder_profile = peoplefinder.get_by_id(sso_email_id=profile.sso_email_id)
        peoplefinder.delete_from_database(peoplefinder_profile=peoplefinder_profile)
    except:
        LogEntry.objects.log_action(
            user_id=profile.sso_email_id,
            content_type_id=None,
            object_id=None,
            object_repr=str(profile),
            change_message="No People finder profile to delete",
            action_flag=DELETION,
        )


def delete_from_sso(profile: Profile) -> None:
    sso_profile = staff_sso.get_by_id(profile.sso_email_id, include_inactive=True)
    staff_sso.delete_from_database(sso_profile=sso_profile)

    all_profiles = get_all_profiles(sso_email_id=profile.sso_email_id)

    # check if combined profile is the only profile left for user
    if [key for key in all_profiles] == ["combined"]:
        combined_profile = combined.get_by_id(
            sso_email_id=profile.sso_email_id, include_inactive=True
        )
        combined.delete_from_database(profile=combined_profile)


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
        all_profile["peoplefinder"] = peoplefinder.get_by_id(sso_email_id=sso_email_id)
    except:
        # no people finder profile found
        pass
    # TODO - more profiles to be added here as we implement more
    return all_profile
