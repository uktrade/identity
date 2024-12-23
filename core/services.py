from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model

from profiles.services.profile import ProfileService
from profiles.services.staff_sso import StaffSSOProfile, StaffSSOService
from user.services.user import UserService


if TYPE_CHECKING:
    from user.models import User
else:
    User = get_user_model()


class CoreService:
    user_service = UserService()
    profile_service = ProfileService()
    sso_profile_service = StaffSSOService()

    def create_user(
        self,
        id: str,
        *args,
        first_name: str = None,
        last_name: str = None,
        preferred_email: str = None,
        emails: list[str] = None,
        **kwargs,
    ) -> tuple[User, bool]:

        user, created = self.user_service.get_or_create_user(id, *args, **kwargs)
        self.profile_service.get_or_create_profile(
            user.sso_email_id,
            user.first_name,
            user.last_name,
            user.preferred_email,
            user.emails,
        )
        self.sso_profile_service.get_or_create_staff_sso_profile(
            user,
            user.first_name,
            user.last_name,
            user.emails,
        )

        return user, created

    def get_user_by_id(self, id: str) -> User:
        return self.user_service.get_user_by_sso_id(id)

    # TODO:
    # - Add create_profile, get_profile etc. in this service
