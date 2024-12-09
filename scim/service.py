from core.service import CoreService

from .schema import SCIMUser


class SCIMService:
    core_service = CoreService()
    # create and return a dictionary for these functions, this will be mapped to the SCIMUser
    # when the api call happens we will map these to the SCIMUser response.

    def get_or_create_user(self, scim_user: SCIMUser) -> tuple[dict, bool]:
        scim_user_details = {
            "is_active": scim_user.active,
            "username": scim_user.externalId,
        }
        return self.core_service.get_or_create_user(
            id=scim_user.externalId,
            **scim_user_details,
        )

    def get_user_by_id(self, id: str) -> dict:
        return self.core_service.get_user_by_id(id)
