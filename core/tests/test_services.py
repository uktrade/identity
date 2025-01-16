import pytest

from core import services
from profiles.models.combined import Profile
from user.exceptions import UserExists
from user.models import User


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("basic_user", [None])
def test_create_identity(mocker):
    mock_user_create = mocker.patch("user.services.create")
    mock_profiles_create = mocker.patch(
        "profiles.services.create_from_sso",
        return_value="__profile__",
    )
    # User is created
    profile = services.create_identity(
        id="john.sso.email.id@gov.uk",
        first_name="Billy",
        last_name="Bob",
        all_emails=[
            "test@test.com",
            "test2@test.com",
            "test3@test.com",
        ],
        primary_email="test2@test.com",
        contact_email="test3@test.com",
    )
    mock_user_create.assert_called_once_with(
        sso_email_id="john.sso.email.id@gov.uk",
    )
    mock_profiles_create.assert_called_once_with(
        sso_email_id="john.sso.email.id@gov.uk",
        first_name="Billy",
        last_name="Bob",
        all_emails=[
            "test@test.com",
            "test2@test.com",
            "test3@test.com",
        ],
        primary_email="test2@test.com",
        contact_email="test3@test.com",
    )
    assert profile == "__profile__"


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


def test_update_identity() -> None:
    profile = services.create_identity(
        "new_user@gov.uk",
        "Billy",
        "Bob",
        ["new_user@email.gov.uk"],
    )
    assert User.objects.get(sso_email_id="new_user@gov.uk").is_active

    services.update_identity(
        profile,
        first_name="Joe",
        last_name="Bobby",
        all_emails=["new_user@email.gov.uk"],
        is_active=False,
    )
    profile.refresh_from_db()

    assert profile.first_name == "Joe"
    assert profile.last_name == "Bobby"
    assert not User.objects.get(sso_email_id="new_user@gov.uk").is_active


def test_delete_identity() -> None:
    profile = services.create_identity(
        "new_user@gov.uk",
        "Billy",
        "Bob",
        ["new_user@email.gov.uk"],
    )

    services.delete_identity(
        profile,
    )
    with pytest.raises(Profile.DoesNotExist) as pex:
        services.get_by_id(
            id=profile.sso_email_id,
        )

    assert str(pex.value.args[0]) == "Profile matching query does not exist."

    with pytest.raises(User.DoesNotExist) as uex:
        User.objects.get(sso_email_id="new_user@gov.uk")

    assert str(uex.value.args[0]) == "User matching query does not exist."
