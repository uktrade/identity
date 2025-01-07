from typing import TYPE_CHECKING, Optional

from django.contrib.admin.models import ADDITION, CHANGE, LogEntry
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.auth import get_user_model

from profiles.models.generic import Email
from profiles.models.staff_sso import StaffSSOProfile, StaffSSOProfileEmail
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
    return StaffSSOProfile.objects.get(user__sso_email_id=sso_email_id)


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
    sso_email_id: str,
    first_name: str,
    last_name: str,
    all_emails: list[str],
    primary_email: Optional[str] = None,
    contact_email: Optional[str] = None,
    reason: Optional[str] = None,
    requesting_user: Optional[User] = None,
) -> StaffSSOProfile:
    if primary_email is not None and primary_email not in all_emails:
        raise ValueError("primary_email not in all_emails")
    if contact_email is not None and contact_email not in all_emails:
        raise ValueError("contact_email not in all_emails")

    staff_sso_profile = get_by_id(sso_email_id)
    update_fields = []
    if first_name is not None:
        update_fields.append("first_name")
        staff_sso_profile.first_name = first_name
    if last_name is not None:
        update_fields.append("last_name")
        staff_sso_profile.last_name = last_name

    # create staff sso email records
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
    return staff_sso_profile.save(update_fields=update_fields)


###############################################################
# Email data methods
###############################################################


def set_email_details(
    profile: StaffSSOProfile,
    email: Email,
    is_primary: Optional[bool] = None,
    is_contact: Optional[bool] = None,
) -> None:
    """
    Update a staff sso email
    """
    staff_sso_profile_email, _ = StaffSSOProfileEmail.objects.get_or_create(
        email=email, profile=profile
    )

    update_fields = []
    if is_primary:
        # ensure only one is marked as primary
        profile.emails.filter(is_primary=True).exclude(email=email).update(
            is_primary=False
        )
        staff_sso_profile_email.is_primary = is_primary
        update_fields.append("is_primary")
    if is_contact:
        # ensure only one is marked as contact
        profile.emails.filter(is_primary=True).exclude(email=email).update(
            is_contact=False
        )
        staff_sso_profile_email.is_contact = is_contact
        update_fields.append("is_contact")

    if len(update_fields) > 0:
        staff_sso_profile_email.save(update_fields=update_fields)
