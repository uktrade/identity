from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model

from profiles import services as profile_service
from user import services as user_service


if TYPE_CHECKING:
    from user.models import User
else:
    User = get_user_model()


def create_user(id: str, initiator: str = "SSO", **kwargs) -> User:
    """
    Entrypoint for new user creation. Triggers the creation of User record,
    then the relevant Profile record as well as a combined Profile.
    """
    user = user_service.create(sso_email_id=id)
    if initiator == "SSO":
        first_name = kwargs.get("first_name", None)
        last_name = kwargs.get("last_name", None)
        emails = kwargs.get("emails", None)
        profile_service.create_from_sso(user, first_name, last_name, emails, )
    return user
