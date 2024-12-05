from django.contrib.auth import get_user_model

from core.schemas.scim_schema import SCIMUser
from user.services.user import User, UserService


class CoreService:
    user_service = UserService()

    def get_user(self, id: int) -> get_user_model:
        return self.user_service.get_user(id)

    def create_user(self, scim_user: SCIMUser) -> tuple[get_user_model, bool]:
        user, created = self.user_service.create_user(scim_user)
        return user, created

    # def create_profile, get_profile etc. in this service
    # SCIM service (in SCIM app) will call the functions from CoreService
