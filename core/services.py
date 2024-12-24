from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model

from profiles import services as profile_services
from profiles.models import ProfileTypes
from profiles.models.staff_sso import StaffSSOProfile
from profiles.services import staff_sso as staff_sso_services
from user import services as user_services


if TYPE_CHECKING:
    from user.models import User
else:
    User = get_user_model()


def new_user(
    id: str,
    initiator: str,
    # TODO: DISCUSS: Should this be better typed as a TypedDict depending on which profile type
    # is being created?
    profile_data: dict,
) -> User:
    """
    Entrypoint for new user creation. Triggers the creation of User record,
    then the relevant Profile record as well as a combined Profile.
    """
    initiating_type = ProfileTypes(initiator)

    try:
        user = user_services.get_by_id(id)
    except User.DoesNotExist:
        user = user_services.create(sso_email_id=id)

    if initiating_type == ProfileTypes.STAFF_SSO:
        first_name: str = profile_data["first_name"]
        last_name: str = profile_data["last_name"]
        emails: list[dict] = profile_data["emails"]
        preferred_email: str | None = profile_data["preferred_email"]
        profile_services.create_from_sso(
            id,
            first_name,
            last_name,
            emails,
            preferred_email,
        )

    return user
