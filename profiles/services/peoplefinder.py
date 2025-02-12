from typing import TYPE_CHECKING, Optional

from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.auth import get_user_model

from profiles.models import PeopleFinderProfile


if TYPE_CHECKING:
    from user.models import User
else:
    User = get_user_model()


def get_profile_completion(peoplefinder_profile):
    # TODO this is a temporary implementation, needs to be done properly
    return 0


def get_by_id(sso_email_id: str) -> PeopleFinderProfile:
    # TODO - This is a temporary implementation just to get tests going. It will be revisited in get People Finder service ticket
    user = User.objects.get(sso_email_id=sso_email_id)
    return PeopleFinderProfile.objects.get(user=user)


def delete_from_database(
    peoplefinder_profile: PeopleFinderProfile,
    reason: Optional[str] = None,
    requesting_user: Optional[User] = None,
) -> None:
    """Really delete a People Finder Profile"""
    if reason is None:
        reason = "Deleting People Finder Profile record"
    requesting_user_id = "via-api"
    if requesting_user is not None:
        requesting_user_id = requesting_user.pk
    LogEntry.objects.log_action(
        user_id=requesting_user_id,
        content_type_id=get_content_type_for_model(peoplefinder_profile).pk,
        object_id=peoplefinder_profile.pk,
        object_repr=str(peoplefinder_profile),
        change_message=reason,
        action_flag=DELETION,
    )

    peoplefinder_profile.delete()
