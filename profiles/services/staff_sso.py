from typing import TYPE_CHECKING, Optional

from django.contrib.auth import get_user_model

from profiles.models.generic import Email, EmailTypes
from profiles.models.staff_sso import StaffSSOProfile, StaffSSOProfileEmail
from user import services as user_services


if TYPE_CHECKING:
    from user.models import User
else:
    User = get_user_model()


###############################################################
# SSO Profile data methods
###############################################################


def get_by_user_id(sso_email_id: str) -> StaffSSOProfile:
    """
    Retrieve a profile by its User ID, only if the user is not soft-deleted.
    """
    # @TODO update the below query (inc the model) to stop it requiring a JOIN
    return StaffSSOProfile.objects.get(user_id=sso_email_id, user__is_active=True)


def create(
    sso_email_id: str,
    first_name: str,
    last_name: str,
    emails: list[dict],
) -> StaffSSOProfile:
    """
    Create a new staff sso profile for the specified request.
    """

    user = user_services.get_by_id(sso_email_id)
    staff_sso_profile = StaffSSOProfile.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
    )
    # FIXME: We don't have complex email data to create the email
    # eg. we don't know when the preferred email will be True(?)
    for email in emails:
        associate_email(
            profile=staff_sso_profile,
            email_address=email["address"],
            type=email["type"],
            preferred=email["preferred"],
        )

    return staff_sso_profile


def update(
    id: str,
    first_name: Optional[str],
    last_name: Optional[str],
    emails: list[dict],
) -> None:
    staff_sso_profile = get_by_user_id(id)
    staff_sso_profile.first_name = first_name
    staff_sso_profile.last_name = last_name

    # create staff sso email records
    for email in emails:
        email_object, _ = Email.objects.get_or_create(
            address=email["address"],
        )
        update_email_details(
            profile=staff_sso_profile,
            email=email_object,
            type=email["type"],
            preferred=email["preferred"],
        )

    staff_sso_profile.save(
        update_fields=(
            "first_name",
            "last_name",
        )
    )


###############################################################
# Email data methods
###############################################################


def associate_email(
    profile: StaffSSOProfile,
    email_address: str,
    type: str = str(EmailTypes.WORK),
    preferred: bool = False,
) -> StaffSSOProfileEmail:
    """
    Ensures that an email is associated with a staff sso profile.
    """
    email_object, _ = Email.objects.get_or_create(
        address=email_address,
    )
    staff_sso_email, _ = StaffSSOProfileEmail.objects.get_or_create(
        profile=profile,
        email=email_object,
        type=type,
        preferred=preferred,
    )
    return staff_sso_email


def update_email_details(
    profile: StaffSSOProfile,
    email: Email,
    type: Optional[str] = None,
    preferred: Optional[bool] = None,
) -> None:
    """
    Update a staff sso email
    """
    staff_sso_profile_email = StaffSSOProfileEmail.objects.get(
        email=email, profile=profile
    )

    update_fields = [
        "profile",
        "email",
    ]
    if type is not None:
        staff_sso_profile_email.type = type
        update_fields.append("type")
    if preferred is not None:
        staff_sso_profile_email.preferred = preferred
        update_fields.append("preferred")

    staff_sso_profile_email.save(update_fields=update_fields)
