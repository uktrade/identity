from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model

from user.exceptions import UserIsDeleted


if TYPE_CHECKING:
    from user.models import User
else:
    User = get_user_model()


class UserService:

    def get_or_create_user(self, sso_email_id, *args, **kwargs) -> tuple[User, bool]:
        """
        Create a new user with the specified username.
        """
        return User.objects.get_or_create(sso_email_id=sso_email_id, *args, **kwargs)

    def get_user_by_sso_id(self, sso_email_id: str) -> User:
        """
        Retrieve a user by their ID, only if the user is not soft-deleted.
        """
        try:
            user = User.objects.get(sso_email_id=sso_email_id)
            if user.is_active:
                return user
            else:
                raise UserIsDeleted("User has been previously deleted")

        except User.DoesNotExist:
            raise User.DoesNotExist("User does not exist")

    def update_user(
        self,
        user: User,
        is_active: bool = True,
        is_staff: bool = True,
        is_superuser: bool = True,
    ) -> User:
        """
        Update a given Django user instance with the provided keyword arguments.
        """
        user.is_active = is_active
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save()
        return user

    def delete_user(self, sso_email_id: str) -> User:
        """
        Soft delete a user by setting the 'is_active' flag to False.
        """
        user = self.get_user_by_sso_id(sso_email_id)
        user.is_active = False
        user.save()
        return user
