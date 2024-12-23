# This is the entrypoint service that coordinates between the sub-services
# If in doubt about what to use, you should probably be using this

from profiles.services import combined, staff_sso
from user.models import User


def generate_combined_profile_fields(sso_email_id: str):
    """
    Figures out which info we have in specific profiles and runs through the
    field hierarchy per data type to generate the values for the combined.
    create method
    """
    raise NotImplementedError()


def create_from_sso(
    sso_email_id: str,
    first_name: str,
    last_name: str,
    emails: list[str],
    preferred_email: str | None = None,
):
    """A central function to create all relevant profile details"""
    combined.create(
        sso_email_id,
        first_name,
        last_name,
        emails,
        preferred_email,
    )
    staff_sso.create(
        sso_email_id,
        first_name,
        last_name,
        emails,
    )
    # staff_sso.create()
    # payload = generate_combined_profile_values()
    # combined.create(sso_user_id, **payload)
    raise NotImplementedError()
