from typing import Optional

from profiles.exceptions import ProfileExists, ProfileIsArchived, ProfileIsNotArchived
from profiles.models import Profile


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
    emails: list[str],
    preferred_email: Optional[str],
) -> Profile:
    try:
        get_by_id(sso_email_id)
    except Profile.DoesNotExist:
        return Profile.objects.create(
            sso_email_id=sso_email_id,
            first_name=first_name,
            last_name=last_name,
            emails=emails,
            preferred_email=preferred_email,
        )
    raise ProfileExists("Profile has been previously created")


#### Standard profile-object methods ####


def update(
    profile: Profile,
    first_name: Optional[str],
    last_name: Optional[str],
    preferred_email: Optional[str],
    emails: Optional[list[str]],
):
    update_fields = []
    if first_name is not None:
        update_fields.append("first_name")
        profile.first_name = first_name
    if last_name is not None:
        update_fields.append("last_name")
        profile.last_name = last_name
    if preferred_email is not None:
        update_fields.append("preferred_email")
        profile.preferred_email = preferred_email
    if emails is not None:
        update_fields.append("emails")
        profile.emails = emails
    return profile.save(update_fields=update_fields)


def archive(profile: Profile):
    """Soft-delete a profile"""
    if not profile.is_active:
        raise ProfileIsArchived("Profile is already archived")

    profile.is_active = False
    return profile.save(update_fields=("is_active",))


def unarchive(profile: Profile):
    """Restore a soft-deleted profile."""
    if profile.is_active:
        raise ProfileIsNotArchived("Profile is not archived")

    profile.is_active = True
    return profile.save(update_fields=("is_active",))


def delete_from_database(profile: Profile):
    """Really delete a Profile. Only to be used in data cleaning (i.e. non-standard) operations"""
    return profile.delete()
