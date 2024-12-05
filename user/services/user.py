from django.contrib.auth import get_user_model

from core.schemas.scim_schema import SCIMUser


User = get_user_model()


class UserService:
    def create_user(self, scim_user: SCIMUser) -> tuple[get_user_model, bool]:
        """
        Create a new user with the specified username.
        """
        user, created = User.objects.get_or_create(
            username=scim_user.externalId,
            is_active=scim_user.active,
            is_staff=False,
            is_superuser=False,
        )
        return user, created

    def get_user(self, id: int) -> get_user_model:
        """
        Retrieve a user by their ID, only if the user is not soft-deleted.
        """
        try:
            user = User.objects.get(id=id, is_active=True)
            return user
        except User.DoesNotExist:
            return None

    def search_users(self, args: dict) -> list[get_user_model]:
        """
        Search users by dynamic filter args
        """
        users = User.objects.filter(**args)
        return users

    def update_user(self, user_id: int, scim_user: SCIMUser) -> get_user_model:
        """
        Update an existing user. At least one field must be provided.
        """
        try:
            user = User.objects.get(id=user_id)
            user.username = scim_user.externalId
            user.is_active = scim_user.active
            user.save()
            return user
        except User.DoesNotExist:
            return None

    def delete_user(self, user_id: int) -> get_user_model:
        """
        Soft delete a user by setting the 'is_active' flag to False.
        """
        try:
            user = User.objects.get(id=user_id, is_active=True)
            user.is_active = False
            user.save()
            return user
        except User.DoesNotExist:
            return None
