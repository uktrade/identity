from typing import TYPE_CHECKING, Optional

from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.auth import get_user_model

from user.exceptions import UserExists, UserIsArchived, UserIsNotArchived


if TYPE_CHECKING:
    from user.models import User
else:
    User = get_user_model()


###############################################################
# Base data methods
###############################################################


#### ID is required - no getting around it ####


def get_by_id(sso_email_id: str, include_inactive: bool = False) -> User:
    """
    Retrieve a user by their ID.
    """
    try:
        user = User.objects.get(sso_email_id=sso_email_id)
        if user.is_active or include_inactive:
            return user
        else:
            raise UserIsArchived("User has been previously archived")

    except User.DoesNotExist:
        raise User.DoesNotExist("User does not exist")


def create(
    sso_email_id: str,
    is_active: bool,
    is_staff: bool = False,
    is_superuser: bool = False,
    reason: Optional[str] = None,
    requesting_user: Optional[User] = None,
) -> User:
    """Simplest and most common version of user creation"""
    try:
        get_by_id(sso_email_id)
    except User.DoesNotExist:
        user = User.objects.create_user(
            sso_email_id=sso_email_id,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )

        if reason is None:
            reason = "Creating new User record"
        requesting_user_id = "via-api"
        if requesting_user is not None:
            requesting_user_id = requesting_user.pk
        LogEntry.objects.log_action(
            user_id=requesting_user_id,
            content_type_id=get_content_type_for_model(user).pk,
            object_id=user.pk,
            object_repr=str(user),
            change_message=reason,
            action_flag=ADDITION,
        )

        return user
    raise UserExists("User has been previously created")


#### Standard user-object methods ####


def update(
    user: User,
    is_staff: bool = False,
    is_superuser: bool = False,
    reason: Optional[str] = None,
    requesting_user: Optional[User] = None,
) -> None:
    """
    Update method allowing only the right fields to be set in this way.
    To change is_active use the dedicated method. ID may not be updated.
    """
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.save(
        update_fields=(
            "is_staff",
            "is_superuser",
        )
    )

    if reason is None:
        reason = "Updating User record: is_staff, is_superuser"
    requesting_user_id = "via-api"
    if requesting_user is not None:
        requesting_user_id = requesting_user.pk
    LogEntry.objects.log_action(
        user_id=requesting_user_id,
        content_type_id=get_content_type_for_model(user).pk,
        object_id=user.pk,
        object_repr=str(user),
        change_message=reason,
        action_flag=CHANGE,
    )


def archive(
    user: User, reason: Optional[str] = None, requesting_user: Optional[User] = None
) -> None:
    """Simplest and most common version of user soft deletion"""
    if not user.is_active:
        raise UserIsArchived("User is already archived")

    if reason is None:
        reason = "Archiving User record"
    requesting_user_id = "via-api"
    if requesting_user is not None:
        requesting_user_id = requesting_user.pk
    LogEntry.objects.log_action(
        user_id=requesting_user_id,
        content_type_id=get_content_type_for_model(user).pk,
        object_id=user.pk,
        object_repr=str(user),
        change_message=reason,
        action_flag=CHANGE,
    )

    user.is_active = False
    user.save(update_fields=("is_active",))


def unarchive(
    user: User, reason: Optional[str] = None, requesting_user: Optional[User] = None
) -> None:
    """Simplest and most common version of user reactivation"""
    if user.is_active:
        raise UserIsNotArchived("User is not archived")

    if reason is None:
        reason = "Unarchiving User record"
    requesting_user_id = "via-api"
    if requesting_user is not None:
        requesting_user_id = requesting_user.pk
    LogEntry.objects.log_action(
        user_id=requesting_user_id,
        content_type_id=get_content_type_for_model(user).pk,
        object_id=user.pk,
        object_repr=str(user),
        change_message=reason,
        action_flag=CHANGE,
    )

    user.is_active = True
    user.save(update_fields=("is_active",))


def delete_from_database(
    user: User, reason: Optional[str] = None, requesting_user: Optional[User] = None
) -> None:
    """Really delete a User"""
    if reason is None:
        reason = "Deleting User record"
    requesting_user_id = "via-api"
    if requesting_user is not None:
        requesting_user_id = requesting_user.pk
    LogEntry.objects.log_action(
        user_id=requesting_user_id,
        content_type_id=get_content_type_for_model(user).pk,
        object_id=user.pk,
        object_repr=str(user),
        change_message=reason,
        action_flag=DELETION,
    )

    user.delete()


###############################################################
# Utility methods
###############################################################


def update_by_id(
    sso_email_id: str, is_staff: bool = False, is_superuser: bool = False
) -> None:
    user = get_by_id(sso_email_id)
    return update(user, is_staff, is_superuser)


def archive_by_id(sso_email_id: str) -> None:
    user = get_by_id(sso_email_id)
    return archive(user)


def unarchive_by_id(sso_email_id: str) -> None:
    user = get_by_id(sso_email_id)
    return unarchive(user)


def delete_from_database_by_id(sso_email_id: str) -> None:
    user = get_by_id(sso_email_id)
    return delete_from_database(user)
