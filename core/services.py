from profiles import services as profile_services
from profiles.models.combined import Profile
from profiles.services import combined, staff_sso, update_from_sso
from user import services as user_services
from user.models import User


def create_identity(
    id: str,
    first_name: str,
    last_name: str,
    all_emails: list[str],
    primary_email: str | None = None,
    contact_email: str | None = None,
) -> Profile:
    """
    Entrypoint for new user creation. Triggers the creation of User record,
    then the relevant Profile record as well as a combined Profile.

    Returns the combined Profile
    """

    user_services.create(sso_email_id=id)
    return profile_services.create_from_sso(
        sso_email_id=id,
        first_name=first_name,
        last_name=last_name,
        all_emails=all_emails,
        contact_email=contact_email,
        primary_email=primary_email,
    )


def update_identity(
    id: str,
    first_name: str,
    last_name: str,
    all_emails: list[str],
    is_active: bool | None = None,
    primary_email: str | None = None,
    contact_email: str | None = None,
) -> Profile:
    """
    Function for updating an existing user (archive / unarchive) and their profile information.

    Returns the combined Profile
    """

    user = user_services.get_by_id(id)
    if not is_active:
        user_services.archive(user)
    else:
        user_services.unarchive(user)

    return profile_services.update_from_sso(
        sso_email_id=id,
        first_name=first_name,
        last_name=last_name,
        all_emails=all_emails,
        primary_email=primary_email,
        contact_email=contact_email,
    )
