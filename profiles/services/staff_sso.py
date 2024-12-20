from typing import Optional

from profiles.models import Email, Profile, StaffSSOProfile, StaffSSOProfileEmail
from user.models import User


def get_or_create_staff_sso_profile(
    user: User,
    first_name: str,
    last_name: str,
    emails: list[dict],
) -> tuple[StaffSSOProfile, bool]:
    """
    Create a new staff sso profile for the specified request.
    """
    staff_sso_profile, profile_created = StaffSSOProfile.objects.get_or_create(
        user=user,
        first_name=first_name,
        last_name=last_name,
    )

    # create staff sso email records
    for email in emails:
        email_object, email_created = Email.objects.get_or_create(
            address=email["address"],
        )
        get_or_create_staff_sso_email(
            profile=staff_sso_profile,
            email=email_object,
            type=email["type"],
            preferred=email["preferred"],
        )

    return staff_sso_profile, profile_created


def get_or_create_staff_sso_email(
    profile: StaffSSOProfile,
    email: StaffSSOProfileEmail,
    type: str,
    preferred: bool,
) -> tuple[StaffSSOProfileEmail, bool]:
    """
    Create a new staff sso email
    """
    staff_sso_email, created = StaffSSOProfileEmail.objects.get_or_create(
        profile=profile,
        email=email,
        type=type,
        preferred=preferred,
    )
    return staff_sso_email, created


def update_staff_sso_email(
    profile: StaffSSOProfile,
    email: StaffSSOProfileEmail,
    type: str,
    preferred: bool,
) -> StaffSSOProfileEmail:
    """
    Create a new staff sso email
    """
    staff_sso_profile_email = StaffSSOProfileEmail.objects.filter(email=email)[0]

    staff_sso_profile_email.profile = profile
    staff_sso_profile_email.email = email
    staff_sso_profile_email.type = type
    staff_sso_profile_email.preferred = preferred

    staff_sso_profile_email.save()
    return staff_sso_profile_email


def get_staff_sso_profile_by_id(id: int) -> StaffSSOProfile:
    """
    Retrieve a user by their ID, only if the user is not soft-deleted.
    """
    return StaffSSOProfile.objects.get(id=id)


def update_staff_sso_profile(
    id: int,
    first_name: Optional[str],
    last_name: Optional[str],
    emails: list[dict],
) -> Profile:

    staff_sso_profile = get_staff_sso_profile_by_id(id)
    staff_sso_profile.first_name = first_name
    staff_sso_profile.last_name = last_name

    # create staff sso email records
    for email in emails:
        email_object, _ = Email.objects.get_or_create(
            address=email["address"],
        )
        update_staff_sso_email(
            profile=staff_sso_profile,
            email=email_object,
            type=email["type"],
            preferred=email["preferred"],
        )

    staff_sso_profile.save()
    return staff_sso_profile
