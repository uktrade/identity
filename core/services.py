from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model

from profiles import services as profile_services
from profiles.models.combined import Profile
from profiles.models.generic import EmailObject
from user import services as user_services


def create_identity(
    id: str,
    first_name: str,
    last_name: str,
    emails: list[EmailObject],
    contact_email: str | None = None,
) -> Profile:
    """
    Entrypoint for new user creation. Triggers the creation of User record,
    then the relevant Profile record as well as a combined Profile.

    Returns the combined Profile
    """

    user_services.create(sso_email_id=id)
    return profile_services.create_from_sso(
        id,
        first_name,
        last_name,
        emails,
        contact_email,
    )
