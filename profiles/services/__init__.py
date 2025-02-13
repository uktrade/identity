# This is the entrypoint service that coordinates between the sub-services
# If in doubt about what to use, you should probably be using this
from typing import Optional

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
    first_name: str | None = None,
    last_name: str | None = None,
    preferred_first_name: str | Unset | None = None,
    pronouns: str | Unset | None = None,
    name_pronunciation: str | Unset | None = None,
    email: str | Unset | None = None,
    contact_email: str | Unset | None = None,
    primary_phone_number: str | Unset | None = None,
    secondary_phone_number: str | Unset | None = None,
    photo: str | Unset | None = None,
    photo_small: str | Unset | None = None,
    grade: str | Unset | None = None,
    manager: PeopleFinderProfile | Unset | None = None,
    not_employee: bool | Unset | None = None,
    workdays: list[str] | Unset | None = None,
    remote_working: str | Unset | None = None,
    usual_office_days: str | Unset | None = None,
    uk_office_location: UkStaffLocation | Unset | None = None,
    location_in_building: str | Unset | None = None,
    international_building: str | Unset | None = None,
    country: Country | Unset | None = None,
    professions: list[str] | Unset | None = None,
    additional_roles: list[str] | Unset | None = None,
    other_additional_roles: str | Unset | None = None,
    key_skills: list[str] | Unset | None = None,
    other_key_skills: str | Unset | None = None,
    learning_interests: list[str] | Unset | None = None,
    other_learning_interests: str | Unset | None = None,
    fluent_languages: str | Unset | None = None,
    intermediate_languages: str | Unset | None = None,
    previous_experience: str | Unset | None = None,
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
    # TODO - more profiles to be added here as we implement more
    return all_profile
