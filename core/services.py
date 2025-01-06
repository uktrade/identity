from profiles import services as profile_services
from profiles.models.combined import Profile
from profiles.services import combined, staff_sso
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


def update_identity_user(
    id: str,
    is_active: bool | None = None,
) -> User:

    user = user_services.get_by_id(id)
    if not is_active:
        user_services.archive(user)
    else:
        user_services.unarchive(user)
    return user


def update_identity_profile(
    id: str,
    first_name: str | None = None,
    last_name: str | None = None,
    emails: list[dict] | None = None,
    preferred_email: str | None = None,
) -> Profile:
    profile = profile_services.get_by_id(id)

    staff_sso.update(
        id,
        first_name,
        last_name,
        emails,
    )
    sso_profile = staff_sso.get_by_user_id(id)
    combined.update(
        profile, first_name, last_name, preferred_email, []  # sso_profile.emails,
    )
    return profile
