from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model

from user.services.user import UserService


if TYPE_CHECKING:
    from user.models import User
else:
    User = get_user_model()


class CoreService:
    user_service = UserService()

    def get_or_create_user(self, id: str, *args, **kwargs) -> tuple[User, bool]:
        return self.user_service.get_or_create_user(id, *args, **kwargs)

    def get_user_by_id(self, id: str) -> User:
        return self.user_service.get_user_by_sso_id(id)

    # TODO:
    # - Add create_profile, get_profile etc. in this service
