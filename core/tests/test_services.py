import pytest

from core import services
from profiles.models.combined import Profile
from profiles.services import staff_sso, update_from_sso
from user.exceptions import UserExists
from user.models import User


pytestmark = pytest.mark.django_db


def test_existing_user(basic_user) -> None:
    with pytest.raises(UserExists):
        services.create_identity(
            id=basic_user.pk,
            first_name="Billy",
            last_name="Bob",
            all_emails=["new_user@email.gov.uk"],
        )


def test_new_user() -> None:
    profile = services.create_identity(
        id="new_user@gov.uk",
        first_name="Billy",
        last_name="Bob",
        all_emails=["new_user@email.gov.uk"],
    )
    assert isinstance(profile, Profile)
    assert profile.pk
    assert profile.sso_email_id == "new_user@gov.uk"
    assert User.objects.get(sso_email_id="new_user@gov.uk")


def test_update_profile() -> None:
    profile = services.create_identity(
        "new_user@gov.uk",
        "Billy",
        "Bob",
        ["new_user@email.gov.uk"],
    )
    sso_profile = staff_sso.get_by_id(profile.sso_email_id)
    print(sso_profile)

    updated_profile = services.update_identity(
        profile.sso_email_id,
        first_name="Joe",
        last_name="Bobby",
        all_emails=["new_user@email.gov.uk"],
        is_active=True,
    )

    assert updated_profile.first_name == "Joe"
    assert updated_profile.last_name == "Bobby"
