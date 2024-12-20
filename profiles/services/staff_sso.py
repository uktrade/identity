from typing import TYPE_CHECKING, Optional

from django.contrib.auth import get_user_model

from profiles.models import (
    EMAIL_TYPE_WORK,
    EMAIL_TYPES,
    Email,
    Profile,
    StaffSSOProfile,
    StaffSSOProfileEmail,
)


if TYPE_CHECKING:
    from user.models import User
else:
    User = get_user_model()


###############################################################
# SSO Profile data methods
###############################################################


def get_by_user_id(id: str) -> StaffSSOProfile:
    """
    Retrieve a profile by its User ID, only if the user is not soft-deleted.
    """
    # @TODO update the below query (inc the model) to stop it requiring a JOIN
    return StaffSSOProfile.objects.get(user_id=id, user__is_active=True)


def create(
    user: User,
    first_name: str,
    last_name: str,
    emails: list[dict],
) -> StaffSSOProfile:
    """
    Create a new staff sso profile for the specified request.
    """
    staff_sso_profile = StaffSSOProfile.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
    )

    for email in emails:
        create_email(
            profile=staff_sso_profile,
            email_address=email["address"],
            type=email["type"],
            preferred=email["preferred"],
        )

    return staff_sso_profile


def update(
    id: int,
    first_name: Optional[str],
    last_name: Optional[str],
    emails: list[dict],
) -> StaffSSOProfile:
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

    staff_sso_profile.save()
    return staff_sso_profile


###############################################################
# Email data methods
###############################################################


def create_email(
    profile: StaffSSOProfile,
    email_address: str,
    type: str = EMAIL_TYPE_WORK,
    preferred: bool = False,
) -> StaffSSOProfileEmail:
    """
    Create a new staff sso email
    """
    email_object, _ = Email.objects.get_or_create(
        address=email_address,
    )
    return associate_email(
        profile=profile,
        email=email_object,
        type=type,
        preferred=preferred,
    )


def associate_email(
    profile: StaffSSOProfile,
    email: Email,
    type: str = EMAIL_TYPE_WORK,
    preferred: bool = False,
) -> StaffSSOProfileEmail:
    """
    Associate an existing email with a staff sso profile
    """
    staff_sso_email, _ = StaffSSOProfileEmail.objects.get_or_create(
        profile=profile,
        email=email,
        type=type,
        preferred=preferred,
    )
    return staff_sso_email


def update_email_details(
    profile: StaffSSOProfile,
    email: StaffSSOProfileEmail,
    type: Optional[str] = None,
    preferred: Optional[bool] = None,
) -> StaffSSOProfileEmail:
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
        update_fields += [
            "type",
        ]
    if preferred is not None:
        staff_sso_profile_email.preferred = preferred
        update_fields += [
            "preferred",
        ]

    return staff_sso_profile_email.save(update_fields=update_fields)
