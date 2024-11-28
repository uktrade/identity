from django.contrib.auth import get_user_model

from core.schemas.scim_schema import SCIMUser


class UserService:
    @staticmethod
    def get_primary_email(scim_user: SCIMUser) -> str:
        emails = scim_user.emails
        primary_email = [email for email in emails if email.primary][0]
        return primary_email.value

    def createUser(scim_user: SCIMUser) -> tuple[get_user_model, bool]:
        user_model = get_user_model()

        user, created = user_model.objects.get_or_create(
            username=scim_user.externalId,
            is_active=scim_user.active,
            is_staff=False,
            is_superuser=False,
        )

        return user, created
