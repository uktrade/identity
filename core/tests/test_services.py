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


def test_bulk_delete_identity_users_from_sso(mocker) -> None:
    mock_delete_identity = mocker.patch(
        "core.services.delete_identity", return_value=None
    )
    services.create_identity(
        id="sso_user1@gov.uk",
        first_name="Billy",
        last_name="Bob",
        all_emails=["new_user@email.gov.uk"],
    )
    services.create_identity(
        id="sso_user2@gov.uk",
        first_name="Gilly",
        last_name="Bob",
        all_emails=["user@email.gov.uk"],
    )
    id3 = services.create_identity(
        id="sso_user3@gov.uk",
        first_name="Tilly",
        last_name="Bob",
        all_emails=["sso_user3@gov.uk", "user3@email.gov.uk"],
    )

    sso_users = [{"id": "sso_user1@gov.uk"}]
    print("id3 ", id3)
    services.bulk_delete_identity_users_from_sso(sso_users=sso_users)
    mock_delete_identity.assert_called_once_with("sso_user3@gov.uk")


def test_bulk_create_and_update_identity_users_from_sso(mocker) -> None:
    services.create_identity(
        id="sso_user2@gov.uk",
        first_name="Gilly",
        last_name="Bob",
        all_emails=["user@email.gov.uk"],
    )
    mock_create_identity = mocker.patch(
        "core.services.create_identity", return_value="__profile__"
    )
    mock_update_identity = mocker.patch(
        "core.services.update_identity", return_value=None
    )

    sso_users = [
        {
            "id": "sso_user2@gov.uk",
            "first_name": "Jane",
            "last_name": "Doe",
            "is_active": True,
            "emails": ["sso_user2@gov.uk", "user2@email.gov.uk"],
            "email": "sso_user2@gov.uk",
            "contact_email": "user2@gov.uk",
        },
        {
            "id": "sso_user3@gov.uk",
            "first_name": "Alice",
            "last_name": "Smith",
            "is_active": True,
            "emails": ["sso_user3@gov.uk", "user3@email.gov.uk"],
            "email": "sso_user3@gov.uk",
            "contact_email": "user3@gov.uk",
        },
    ]
    services.bulk_create_and_update_identity_users_from_sso(sso_users=sso_users)
    mock_create_identity.assert_called_once_with(
        id="sso_user3@gov.uk",
        first_name="Alice",
        last_name="Smith",
        all_emails=["sso_user3@gov.uk", "user3@email.gov.uk"],
        primary_email="sso_user3@gov.uk",
        contact_email="user3@gov.uk",
    )
    mock_update_identity.assert_called_once_with(
        profile=services.get_by_id("sso_user2@gov.uk"),
        first_name="Jane",
        last_name="Doe",
        all_emails=["sso_user2@gov.uk", "user2@email.gov.uk"],
        is_active=True,
        primary_email="sso_user2@gov.uk",
        contact_email="user2@gov.uk",
    )


def test_sync_bulk_sso_users(mocker) -> None:
    services.create_identity(
        id="sso_user1@gov.uk",
        first_name="Billy",
        last_name="Bob",
        all_emails=["new_user@email.gov.uk"],
    )
    services.create_identity(
        id="sso_user2@gov.uk",
        first_name="Gilly",
        last_name="Bob",
        all_emails=["user@email.gov.uk"],
    )

    mock_get_bulk_user_records = mocker.patch(
        "core.services.get_bulk_user_records_from_sso",
        return_value=[
            {
                "id": "sso_user2@gov.uk",
                "first_name": "Gilly",
                "last_name": "Doe",
                "is_active": True,
                "emails": ["sso_user2@gov.uk", "user2@email.gov.uk"],
                "email": "sso_user2@gov.uk",
                "contact_email": "user2@gov.uk",
            },
        ],
    )
    mock_bulk_delete = mocker.patch(
        "core.services.bulk_delete_identity_users_from_sso", return_value=None
    )

    mock_bulk_create_and_update = mocker.patch(
        "core.services.bulk_create_and_update_identity_users_from_sso",
        return_value=None,
    )
    services.sync_bulk_sso_users()

    mock_bulk_delete.assert_called_once_with(
        sso_users=[
            {
                "id": "sso_user2@gov.uk",
                "first_name": "Gilly",
                "last_name": "Doe",
                "is_active": True,
                "emails": ["sso_user2@gov.uk", "user2@email.gov.uk"],
                "email": "sso_user2@gov.uk",
                "contact_email": "user2@gov.uk",
            },
        ]
    )
    mock_bulk_create_and_update.assert_called_once_with(
        sso_users=[
            {
                "id": "sso_user2@gov.uk",
                "first_name": "Gilly",
                "last_name": "Doe",
                "is_active": True,
                "emails": ["sso_user2@gov.uk", "user2@email.gov.uk"],
                "email": "sso_user2@gov.uk",
                "contact_email": "user2@gov.uk",
            },
        ]
    )

    mock_get_bulk_user_records.assert_called_once()
