from django.contrib.auth import get_user_model

from core.schemas.scim_schema import SCIMUser


class SCIMService:
    def __init__():
        super()

    def transform_user(scim_request: SCIMUser) -> get_user_model:
        user_model = get_user_model()
        user = {
            "username": scim_request.userName,
            "email": scim_request.emails,
            "first_name": scim_request.name.givenName,
            "last_name": scim_request.name.familyName,
            "is_active": scim_request.active,
            "is_superuser": False,
            "is_staff": False,
        }

        user, _ = user_model.objects.get_or_create(
            username=scim_request.userName,
            email=scim_request.emails,
            first_name=scim_request.name.givenName,
            last_name=scim_request.name.familyName,
            is_active=scim_request.active,
            is_superuser=False,
            is_staff=False,
        )

        return user

    def to_scim(user: get_user_model) -> SCIMUser:
        # print(user)
        return {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
            "userName": user.username,
            "name": {
                "givenName": user.first_name,
                "familyName": user.last_name,
            },
            "emails": user.email,
            "active": user.is_active,
        }
