from core.schemas.scim_schema import SCIMUser
from django.contrib.auth import get_user_model


user_model = get_user_model()

class CoreService:
    def get_users() -> list[get_user_model]:
        return user_model.objects.all()

    def create_user(scim_request: SCIMUser) -> tuple[get_user_model, bool]:
        user, created = user_model.objects.get_or_create(scim_request)
        if created:
            return user, 201
        else:
            return user, 200

    def update_user():
        pass
