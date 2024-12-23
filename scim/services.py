from typing import TypedDict

from core.services import CoreService

from .schemas import SCIMUserIn


# TODO:
# - Add profile creation methods here
# - Update the user_dict to have profile data
# - Update the SCIMUser Schema "name" field to work
# with profile name (first_name, last_name ?)


class SCIMService:
    core_service = CoreService()

    def create_user(self, scim_user: SCIMUserIn) -> tuple[dict, bool]:

        preferred_email: str
        for email in scim_user.emails:
            if email.primary:
                preferred_email = email

        user, created = self.core_service.create_user(
            id=scim_user.externalId,
            first_name=scim_user.name.givenName,
            last_name=scim_user.name.familyName,
            preferred_email=preferred_email,
            emails=scim_user.emails,
        )
        user_dict = {
            "sso_email_id": user.sso_email_id,
            "is_active": user.is_active,
        }

        return user_dict, created

    def get_user_by_id(self, id: str) -> dict:
        user = self.core_service.get_user_by_id(id)
        user_dict = {
            "sso_email_id": user.sso_email_id,
            "is_active": user.is_active,
        }
        return user_dict
