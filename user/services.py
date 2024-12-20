from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model

from user.exceptions import UserIsDeleted


if TYPE_CHECKING:
    from user.models import User
else:
    User = get_user_model()


def get_or_create_user(sso_email_id, *args, **kwargs) -> tuple[User, bool]:
    """
    Create a new user with the specified username.
    """
    return User.objects.get_or_create(sso_email_id=sso_email_id, *args, **kwargs)


def get_user_by_sso_id(sso_email_id: str) -> User:
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


def update_user(user: User, **kwargs) -> User:
    """
    Update a given Django user instance with the provided keyword arguments.
    """
    # Validate that only valid fields are being updated
    valid_fields = [
        "sso_email_id",
        "is_active",
        "is_staff",
        "is_superuser",
    ]
    for field in kwargs.keys():
        if field not in valid_fields:
            raise ValueError(f"{field} is not a valid field for User model")

    # Update user attributes with provided keyword arguments
    for field, value in kwargs.items():
        if hasattr(user, field):
            setattr(user, field, value)

    user.save()
    return user


def delete_user(sso_email_id: str) -> User:
    """
    Soft delete a user by setting the 'is_active' flag to False.
    """
    user = get_user_by_sso_id(sso_email_id)
    user.is_active = False
    user.save()
    return user
