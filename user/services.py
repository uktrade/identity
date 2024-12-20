from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model

from user.exceptions import UserAlreadyExists, UserIsArchived


if TYPE_CHECKING:
    from user.models import User
else:
    User = get_user_model()


###############################################################
# Base data methods
###############################################################


#### ID is required - no getting around it ####


def get_by_id(sso_email_id: str):
    """
    Retrieve a user by their ID, only if the user is not soft-deleted.
    """
    try:
        user = User.objects.get(sso_email_id=sso_email_id)
        if user.is_active:
            return user
        else:
            raise UserIsArchived("User has been previously deleted")

    except User.DoesNotExist:
        raise User.DoesNotExist("User does not exist")


def create(sso_email_id: str, is_staff: bool = False, is_superuser: bool = False):
    """Simplest and most common version of user creation"""
    try:
        get_by_id(sso_email_id)
        raise UserAlreadyExists("User has been previously created")
    except User.DoesNotExist:
        return User.objects.create_user(
            sso_email_id=sso_email_id,
            is_active=True,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )


#### Standard user object methods ####


def update(user: User, is_staff: bool = False, is_superuser: bool = False):
    """
    Update method allowing only the right fields to be set in this way.
    To change is_active use the dedicated method. ID may not be updated.
    """
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    return user.save(update_fields=("is_staff", "is_superuser"))


def archive(user: User):
    """Simplest and most common version of user soft deletion"""
    user.is_active = False
    return user.save(update_fields=("is_active",))


def unarchive(user: User):
    """Simplest and most common version of user reactivation"""
    user.is_active = True
    return user.save(update_fields=("is_active",))


def delete_from_database(user: User):
    """Only to be used in data cleaning (i.e. non-standard) operations"""
    return user.delete()


###############################################################
# Utility methods
###############################################################


def update_by_id(sso_email_id: str, is_staff: bool = False, is_superuser: bool = False):
    user = get_by_id(sso_email_id)
    return update(user, is_staff, is_superuser)


def archive_by_id(sso_email_id: str):
    user = get_by_id(sso_email_id)
    return archive(user)


def unarchive_by_id(sso_email_id: str):
    user = get_by_id(sso_email_id)
    return unarchive(user)


def delete_from_database_by_id(sso_email_id: str):
    user = get_by_id(sso_email_id)
    return delete_from_database(user)
