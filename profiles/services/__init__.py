# This is the entrypoint service that coordinates between the sub-services
# If in doubt about what to use, you should probably be using this

from profiles.models.generic import Profile
from profiles.services import combined, staff_sso
from user.models import User


def generate_combined_profile_data(sso_email_id: str):
    """
    Figures out which info we have in specific profiles and runs through the
    field hierarchy per data type to generate the values for the combined.
    create method
    """
    raise NotImplementedError()
    return {
        "first_name": "",
        "last_name": "",
        "preferred_email": "",
        "emails": [],
    }


def create_from_sso(
    sso_email_id: str,
    first_name: str,
    last_name: str,
    emails: list[str],
    preferred_email: str | None = None,
):
    """A central function to create all relevant profile details"""
    staff_sso.create(
        sso_email_id,
        first_name,
        last_name,
        emails,
    )
    combined_profile_data = generate_combined_profile_data()
    try:
        profile = combined.get_by_id(sso_email_id)
    except Profile.DoesNotExist:
        combined.create(
            sso_email_id,
            combined_profile_data["first_name"],
            combined_profile_data["last_name"],
            combined_profile_data["preferred_email"],
            combined_profile_data["emails"],
        )
    else:
        combined.update(
            profile,
            combined_profile_data["first_name"],
            combined_profile_data["last_name"],
            combined_profile_data["preferred_email"],
            combined_profile_data["emails"],
        )
