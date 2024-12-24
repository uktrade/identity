from typing import Optional

from profiles.models.generic import Profile


###############################################################
# Base data methods
###############################################################


#### ID is required - no getting around it ####


def get_by_id(sso_email_id: str) -> Profile:
    return Profile.objects.get(sso_email_id=sso_email_id)


def create(
    sso_email_id: str,
    first_name: str,
    last_name: str,
    emails: list[str],
    preferred_email: Optional[str] = None,
) -> Profile:
    return Profile.objects.create(
        sso_email_id=sso_email_id,
        first_name=first_name,
        last_name=last_name,
        emails=emails,
        preferred_email=preferred_email,
    )


#### Standard profile-object methods ####


def update(
    profile: Profile,
    first_name: Optional[str],
    last_name: Optional[str],
    preferred_email: Optional[str],
    emails: Optional[list[str]],
) -> None:
    profile.first_name = first_name
    profile.last_name = last_name
    profile.preferred_email = preferred_email
    profile.emails = emails
    profile.save(
        update_fields=[
            "first_name",
            "last_name",
            "preferred_email",
            "emails",
        ]
    )


def delete(profile: Profile):
    """
    Retrieve a user by their ID, only if the user is not soft-deleted.
    """
    profile.is_active = False
    return profile.save(update_fields=["is_active"])
