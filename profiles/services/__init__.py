# This is the entrypoint service that coordinates between the sub-services
# If in doubt about what to use, you should probably be using this

from profiles.models.combined import Profile
from profiles.models.generic import EmailObject
from profiles.services import combined, staff_sso

from .combined import get_by_id as get_combined_by_id


def get_by_id(sso_email_id: str) -> Profile:
    return get_combined_by_id(sso_email_id=sso_email_id)


def generate_combined_profile_data(sso_email_id: str):
    """
    Figures out which info we have in specific profiles and runs through the
    field hierarchy per data type to generate the values for the combined.
    create method
    """
    sso_profile = staff_sso.get_by_user_id(sso_email_id)

    return {
        "first_name": sso_profile.first_name,
        "last_name": sso_profile.last_name,
        "preferred_email": sso_profile.contact_email,
        "emails": sso_profile.email_addresses,
    }


def create_from_sso(
    sso_email_id: str,
    first_name: str,
    last_name: str,
    emails: list[EmailObject],
    contact_email: str | None = None,
) -> Profile:
    """A central function to create all relevant profile details"""
    staff_sso.create(
        sso_email_id,
        first_name,
        last_name,
        emails,
    )
    combined_profile_data = generate_combined_profile_data(sso_email_id)

    # We might need a try/except here, if other providers (eg. oracle)
    # are going to do "create" action on the combined profile.
    return combined.create(
        sso_email_id=sso_email_id,
        first_name=combined_profile_data["first_name"],
        last_name=combined_profile_data["last_name"],
        preferred_email=combined_profile_data["preferred_email"],
        emails=combined_profile_data["emails"],
    )
