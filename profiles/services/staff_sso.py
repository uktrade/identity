from typing import TYPE_CHECKING, Optional

from django.contrib.admin.models import ADDITION, CHANGE, LogEntry
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.auth import get_user_model

from profiles.models.generic import Email
from profiles.models.staff_sso import StaffSSOProfile, StaffSSOProfileEmail
from profiles.types import UNSET, Unset
from user import services as user_services


if TYPE_CHECKING:
    from user.models import User
else:
    User = get_user_model()


###############################################################
# SSO Profile data methods
###############################################################


def get_by_id(sso_email_id: str) -> StaffSSOProfile:
    """
    Retrieve a profile by its User ID, only if the user is not soft-deleted.
    """
    return StaffSSOProfile.objects.get(
        user__sso_email_id=sso_email_id, user__is_active=True
    )


def create(
    sso_email_id: str,
    first_name: str,
    last_name: str,
    all_emails: list[str],
    primary_email: Optional[str] = None,
    contact_email: Optional[str] = None,
    reason: Optional[str] = None,
    requesting_user: Optional[User] = None,
) -> StaffSSOProfile:
    """
    Create a new staff sso profile for the specified request.
    """
    if primary_email is not None and primary_email not in all_emails:
        raise ValueError("primary_email not in all_emails")
    if contact_email is not None and contact_email not in all_emails:
        raise ValueError("contact_email not in all_emails")

    user = user_services.get_by_id(sso_email_id=sso_email_id)
    staff_sso_profile = StaffSSOProfile.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
    )

    if reason is None:
        reason = "Creating new StaffSSOProfile"
    requesting_user_id = "via-api"
    if requesting_user is not None:
        requesting_user_id = requesting_user.pk
    LogEntry.objects.log_action(
        user_id=requesting_user_id,
        content_type_id=get_content_type_for_model(staff_sso_profile).pk,
        object_id=staff_sso_profile.pk,
        object_repr=str(staff_sso_profile),
        change_message=reason,
        action_flag=ADDITION,
    )
    for email in all_emails:
        email_object, _ = Email.objects.get_or_create(
            address=email,
        )
        is_primary = None
        if email == primary_email:
            is_primary = True
        is_contact = None
        if email == contact_email:
            is_contact = True

        set_email_details(
            profile=staff_sso_profile,
            email=email_object,
            is_primary=is_primary,
            is_contact=is_contact,
        )

    return staff_sso_profile


def update(
    staff_sso_profile: StaffSSOProfile,
    first_name: Optional[str],
    last_name: Optional[str],
    all_emails: list[str],
    primary_email: str | Unset | None = None,
    contact_email: str | Unset | None = None,
    reason: Optional[str] = None,
    requesting_user: Optional[User] = None,
) -> None:
    if (
        primary_email is not None
        and primary_email is not UNSET
        and primary_email not in all_emails
    ):
        raise ValueError("primary_email not in all_emails")
    if (
        contact_email is not None
        and contact_email is not UNSET
        and contact_email not in all_emails
    ):
        raise ValueError("contact_email not in all_emails")

    update_fields = []
    if first_name is not None:
        update_fields.append("first_name")
        staff_sso_profile.first_name = first_name
    if last_name is not None:
        update_fields.append("last_name")
        staff_sso_profile.last_name = last_name
    staff_sso_profile.save(update_fields=update_fields)

    # add / update staff sso email records
    for email in all_emails:
        email_object, _ = Email.objects.get_or_create(
            address=email,
        )
        is_primary: bool | Unset | None = None
        if primary_email == UNSET:
            is_primary = UNSET
        elif email == primary_email:
            is_primary = True
        is_contact: bool | Unset | None = None
        if contact_email == UNSET:
            is_contact = UNSET
        elif email == contact_email:
            is_contact = True
        set_email_details(
            profile=staff_sso_profile,
            email=email_object,
            is_primary=is_primary,
            is_contact=is_contact,
        )
    # remove emails not in the all_emails list
    staff_sso_profile.emails.exclude(email__address__in=all_emails).delete()

    if reason is None:
        reason = f"Updating StaffSSOProfile record: {", ".join(update_fields)}"
    requesting_user_id = "via-api"
    if requesting_user is not None:
        requesting_user_id = requesting_user.pk
    LogEntry.objects.log_action(
        user_id=requesting_user_id,
        content_type_id=get_content_type_for_model(staff_sso_profile).pk,
        object_id=staff_sso_profile.pk,
        object_repr=str(staff_sso_profile),
        change_message=reason,
        action_flag=CHANGE,
    )


###############################################################
# Email data methods
###############################################################


def set_email_details(
    profile: StaffSSOProfile,
    email: Email,
    is_primary: bool | Unset | None = None,
    is_contact: bool | Unset | None = None,
) -> None:
    """
    Update a staff sso email
    """
    staff_sso_profile_email, _ = StaffSSOProfileEmail.objects.get_or_create(
        email=email, profile=profile
    )

    update_fields = []
    if is_primary is not None:
        # ensure only one is marked as primary
        profile.emails.filter(is_primary=True).exclude(email=email).update(
            is_primary=False
        )
        if is_primary == UNSET:
            staff_sso_profile_email.is_primary = False
        else:
            staff_sso_profile_email.is_primary = True
        update_fields.append("is_primary")
    if is_contact is not None:
        # ensure only one is marked as contact
        profile.emails.filter(is_contact=True).exclude(email=email).update(
            is_contact=False
        )
        if is_contact == UNSET:
            staff_sso_profile_email.is_contact = False
        else:
            staff_sso_profile_email.is_contact = True
        update_fields.append("is_contact")

    if len(update_fields) > 0:
        staff_sso_profile_email.save(update_fields=update_fields)
