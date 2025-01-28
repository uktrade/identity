from typing import TYPE_CHECKING, Optional

from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.auth import get_user_model

from profiles.exceptions import ProfileExists, ProfileIsArchived, ProfileIsNotArchived
from profiles.models.combined import Profile


if TYPE_CHECKING:
    from user.models import User
else:
    User = get_user_model()


###############################################################
# Base data methods
###############################################################


#### ID is required - no getting around it ####


def get_by_id(sso_email_id: str) -> Profile:
    # NB we're not raising more specific exceptions here because we're optimising this for speed
    return Profile.objects.get(sso_email_id=sso_email_id, is_active=True)


def create(
    sso_email_id: str,
    first_name: str,
    last_name: str,
    all_emails: list[str],
    primary_email: Optional[str] = None,
    contact_email: Optional[str] = None,
    reason: Optional[str] = None,
    requesting_user: Optional[User] = None,
) -> Profile:
    """
    Creates a combined Profile object - will set primary email to the first
    in the list of emails if none is provided
    """
    try:
        get_by_id(sso_email_id)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(
            sso_email_id=sso_email_id,
            first_name=first_name,
            last_name=last_name,
            emails=all_emails,
            primary_email=primary_email,
            contact_email=contact_email,
            is_active=True,
        )

        if reason is None:
            reason = "Creating new Profile"
        requesting_user_id = "via-api"
        if requesting_user is not None:
            requesting_user_id = requesting_user.pk
        LogEntry.objects.log_action(
            user_id=requesting_user_id,
            content_type_id=get_content_type_for_model(profile).pk,
            object_id=profile.pk,
            object_repr=str(profile),
            change_message=reason,
            action_flag=ADDITION,
        )

        return profile
    raise ProfileExists("Profile has been previously created")


#### Standard profile-object methods ####


def update(
    profile: Profile,
    first_name: Optional[str],
    last_name: Optional[str],
    all_emails: list[str],
    primary_email: Optional[str] = None,
    contact_email: Optional[str] = None,
    is_active: Optional[bool] = None,
    reason: Optional[str] = None,
    requesting_user: Optional[User] = None,
) -> None:
    update_fields = []
    if first_name is not None:
        update_fields.append("first_name")
        profile.first_name = first_name
    if last_name is not None:
        update_fields.append("last_name")
        profile.last_name = last_name
    if primary_email is not None:
        update_fields.append("primary_email")
        profile.primary_email = primary_email
    if contact_email is not None:
        update_fields.append("contact_email")
        profile.contact_email = contact_email
    if all_emails is not None:
        update_fields.append("emails")
        profile.emails = all_emails

    profile.save(update_fields=update_fields)

    if reason is None:
        reason = f"Updating Profile record: {", ".join(update_fields)}"
    requesting_user_id = "via-api"
    if requesting_user is not None:
        requesting_user_id = requesting_user.pk
    LogEntry.objects.log_action(
        user_id=requesting_user_id,
        content_type_id=get_content_type_for_model(profile).pk,
        object_id=profile.pk,
        object_repr=str(profile),
        change_message=reason,
        action_flag=CHANGE,
    )
    if is_active is not None:
        if is_active:
            if not profile.is_active:
                unarchive(profile)
        else:
            archive(profile)


def archive(
    profile: Profile,
    reason: Optional[str] = None,
    requesting_user: Optional[User] = None,
) -> None:
    """Soft-delete a profile"""
    if not profile.is_active:
        raise ProfileIsArchived("Profile is already archived")

    if reason is None:
        reason = "Archiving Profile record"
    requesting_user_id = "via-api"
    if requesting_user is not None:
        requesting_user_id = requesting_user.pk
    LogEntry.objects.log_action(
        user_id=requesting_user_id,
        content_type_id=get_content_type_for_model(profile).pk,
        object_id=profile.pk,
        object_repr=str(profile),
        change_message=reason,
        action_flag=CHANGE,
    )

    profile.is_active = False
    profile.save(update_fields=("is_active",))


def unarchive(
    profile: Profile,
    reason: Optional[str] = None,
    requesting_user: Optional[User] = None,
) -> None:
    """Restore a soft-deleted profile."""
    if profile.is_active:
        raise ProfileIsNotArchived("Profile is not archived")

    if reason is None:
        reason = "Unarchiving Profile record"
    requesting_user_id = "via-api"
    if requesting_user is not None:
        requesting_user_id = requesting_user.pk
    LogEntry.objects.log_action(
        user_id=requesting_user_id,
        content_type_id=get_content_type_for_model(profile).pk,
        object_id=profile.pk,
        object_repr=str(profile),
        change_message=reason,
        action_flag=CHANGE,
    )

    profile.is_active = True
    profile.save(update_fields=("is_active",))


def delete_from_database(
    profile: Profile,
    reason: Optional[str] = None,
    requesting_user: Optional[User] = None,
) -> None:
    """Really delete a Profile. Useful for data cleaning (i.e. non-standard) operations"""
    if reason is None:
        reason = "Deleting Profile record"
    requesting_user_id = "via-api"
    if requesting_user is not None:
        requesting_user_id = requesting_user.pk
    LogEntry.objects.log_action(
        user_id=requesting_user_id,
        content_type_id=get_content_type_for_model(profile).pk,
        object_id=profile.pk,
        object_repr=str(profile),
        change_message=reason,
        action_flag=DELETION,
    )

    profile.delete()
