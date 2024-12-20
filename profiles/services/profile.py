from typing import Optional

from profiles.models import Profile


def get_or_create_profile(
    sso_email_id: str,
    first_name: str,
    last_name: str,
    preferred_email: str,
    emails: list[str],
    *args,
    **kwargs,
) -> tuple[Profile, bool]:

    profile, created = Profile.objects.get_or_create(
        sso_email_id=sso_email_id,
        first_name=first_name,
        last_name=last_name,
        preferred_email=preferred_email,
        emails=emails,
        *args,
        **kwargs,
    )
    return profile, created

def get_profile_by_sso_email_id(sso_email_id: str) -> Profile:
    """
    Retrieve a user by their ID, only if the user is not soft-deleted.
    """
    return Profile.objects.get(sso_email_id=sso_email_id)

def update_profile(
    sso_email_id: str,
    first_name: Optional[str],
    last_name: Optional[str],
    preferred_email: Optional[str],
    emails: Optional[list[str]],
) -> Profile:
    profile = get_profile_by_sso_email_id(sso_email_id)

    profile.first_name = first_name
    profile.last_name = last_name
    profile.preferred_email = preferred_email
    profile.emails = emails
    profile.save()
    return profile

def delete_profile(sso_email_id: str) -> Profile:
    """
    Retrieve a user by their ID, only if the user is not soft-deleted.
    """
    profile = Profile.objects.get(sso_email_id=sso_email_id)
    profile.is_active = False
    profile.save()
    return profile
