from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model

from profiles import services as profile_services
from user import services as user_services


if TYPE_CHECKING:
    from user.models import User
else:
    User = get_user_model()


def create_identity(
    id: str,
    first_name: str,
    last_name: str,
    emails: list[dict],
    preferred_email: str | None = None,
) -> User:
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
        preferred_email,
    )
