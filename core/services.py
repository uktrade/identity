from profiles import services as profile_services
from profiles.models.combined import Profile
from profiles.types import UNSET, Unset  # noqa
from user import services as user_services
from user.models import User


def get_by_id(id: str):
    return profile_services.get_by_id(sso_email_id=id)


def create_identity(
    id: str,
    first_name: str,
    last_name: str,
    all_emails: list[str],
    primary_email: str | Unset | None = None,
    contact_email: str | Unset | None = None,
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

    Returns the combined Profile
    """

    profile_services.update_from_sso(
        profile=profile,
        first_name=first_name,
        last_name=last_name,
        all_emails=all_emails,
        primary_email=primary_email,
        contact_email=contact_email,
    )

    user = User.objects.get(sso_email_id=profile.sso_email_id)
    if user.is_active != is_active:
        if is_active:
            user_services.unarchive(user)
        else:
            user_services.archive(user)
