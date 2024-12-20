from profiles.models import Email, Profile, StaffSSOProfile, StaffSSOProfileEmail
from user.models import User


def get_or_create_staff_sso_profile(
    user: User,
    first_name: str,
    last_name: str,
    emails: list[dict],
    *args,
    **kwargs,
) -> tuple[StaffSSOProfile, bool]:
    """
    Create a new staff sso profile for the specified request.
    """
    staff_sso_profile, profile_created = StaffSSOProfile.objects.get_or_create(
        user=user, first_name=first_name, last_name=last_name, *args, **kwargs
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
    *args,
    **kwargs,
) -> tuple[StaffSSOProfileEmail, bool]:
    """
    Create a new staff sso email
    """
    staff_sso_email, created = StaffSSOProfileEmail.objects.get_or_create(
        profile=profile,
        email=email,
        type=type,
        preferred=preferred,
        *args,
        **kwargs,
    )
    return staff_sso_email, created


def get_staff_sso_profile_by_id(id: int) -> Profile:
    """
    Retrieve a user by their ID, only if the user is not soft-deleted.
    """
    return StaffSSOProfile.objects.get(id=id)
