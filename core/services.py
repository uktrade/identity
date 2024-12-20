from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model

from user import services as user_services


if TYPE_CHECKING:
    from user.models import User
else:
    User = get_user_model()


def get_or_create_user(id: str, *args, **kwargs) -> tuple[User, bool]:
    return user_services.get_or_create_user(id, *args, **kwargs)


def get_user_by_id(id: str) -> User:
    return user_services.get_user_by_sso_id(id)


# TODO:
# - Add create_profile, get_profile etc. in this service
