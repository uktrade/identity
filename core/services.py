import logging

from profiles import services as profile_services
from profiles.models.combined import Profile
from profiles.types import UNSET, Unset  # noqa
from user import services as user_services
from user.models import User


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

    profile_services.delete_sso_profile(profile=profile)
    profile_services.delete_combined_profile(profile=profile)

    # delete user if no profile exists for user
    all_profiles = profile_services.get_all_profiles(sso_email_id=profile_id)
    if not all_profiles:
        user = user_services.get_by_id(sso_email_id=profile_id, include_inactive=True)
        user_services.delete_from_database(user=user)
