# This is the entrypoint service that coordinates between the sub-services
# If in doubt about what to use, you should probably be using this
from typing import Optional

from django.db import models

from profiles.models.combined import Profile
from profiles.services import combined, staff_sso
from profiles.types import Unset


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
