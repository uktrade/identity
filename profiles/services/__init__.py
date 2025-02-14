# This is the entrypoint service that coordinates between the sub-services
# If in doubt about what to use, you should probably be using this
import logging
from typing import Optional

from django.db import models

from profiles.exceptions import NonCombinedProfileExists
from profiles.models.combined import Profile
from profiles.models.staff_sso import StaffSSOProfile
from profiles.services import combined, staff_sso
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


def delete_combined_profile(profile: Profile) -> None:
    all_profiles = get_all_profiles(sso_email_id=profile.sso_email_id)

    # check and delete if combined profile is the only profile left for user
    if len(all_profiles) == 1 and "combined" in all_profiles:
        combined.delete_from_database(profile=profile)
    else:
        raise NonCombinedProfileExists(f"All existing profiles: {all_profiles.keys}")


def delete_sso_profile(profile: Profile) -> None:
    try:
        sso_profile = staff_sso.get_by_id(profile.sso_email_id, include_inactive=True)
        staff_sso.delete_from_database(sso_profile=sso_profile)
    except StaffSSOProfile.DoesNotExist:
        logger.debug(
            f"Failed to delete SSO profile for {profile.sso_email_id}. SSO profile is already deleted."
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
