from unittest.mock import call

import pytest

from core import services
from core.services import (
    SSO_CONTACT_EMAIL_ADDRESS,
    SSO_EMAIL_ADDRESSES,
    SSO_FIRST_NAME,
    SSO_LAST_NAME,
    SSO_USER_EMAIL_ID,
    SSO_USER_STATUS,
)
from profiles import services as profile_services
from profiles.models.combined import Profile
from user import services as user_services
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
        id="billy.sso.email.id@gov.uk",
        first_name="Billy",
        last_name="Bob",
        all_emails=[
            "test@test.com",
            "test2@test.com",
            "test3@test.com",
        ],
        is_active=False,
        primary_email="test2@test.com",
        contact_email="test3@test.com",
    )
    mock_user_create.assert_called_once_with(
        sso_email_id="billy.sso.email.id@gov.uk",
        is_active=False,
    )
    mock_profiles_create.assert_called_once_with(
        sso_email_id="billy.sso.email.id@gov.uk",
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
            is_active=True,
        )


def test_new_user() -> None:
    profile = services.create_identity(
        id="new_user@gov.uk",
        first_name="Billy",
        last_name="Bob",
        all_emails=["new_user@email.gov.uk"],
        is_active=True,
    )
    assert isinstance(profile, Profile)
    assert profile.pk
    assert profile.sso_email_id == "new_user@gov.uk"
    assert user_services.get_by_id(
        sso_email_id="new_user@gov.uk", include_inactive=True
    )


def test_update_identity() -> None:
    profile = services.create_identity(
        "new_user@gov.uk",
        "Billy",
        "Bob",
        ["new_user@email.gov.uk"],
        is_active=True,
    )
    assert user_services.get_by_id(
        sso_email_id="new_user@gov.uk", include_inactive=True
    ).is_active

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
    assert not user_services.get_by_id(
        sso_email_id="new_user@gov.uk",
        include_inactive=True,
    ).is_active


def test_delete_identity() -> None:
    profile = services.create_identity(
        "new_user@gov.uk",
        "Billy",
        "Bob",
        ["new_user@email.gov.uk"],
        is_active=True,
    )

    services.delete_identity(
        profile,
    )
    with pytest.raises(Profile.DoesNotExist) as pex:
        services.get_profile_by_id(
            id=profile.sso_email_id,
            include_inactive=True,
        )

    assert str(pex.value.args[0]) == "Profile matching query does not exist."

    with pytest.raises(User.DoesNotExist) as uex:
        user_services.get_by_id(
            sso_email_id="new_user@gov.uk",
            include_inactive=True,
        )

    assert str(uex.value.args[0]) == "User matching query does not exist."


@pytest.mark.usefixtures("sso_profile", "combined_profile")
def test_bulk_delete_identity_users_from_sso(mocker) -> None:
    id = "sso_user1@gov.uk"
    id_2 = "sso_user2@gov.uk"
    id_3 = "sso_user3@gov.uk"
    services.create_identity(
        id=id,
        first_name="Billy",
        last_name="Bob",
        all_emails=["new_user@email.gov.uk"],
        is_active=True,
    )
    services.create_identity(
        id=id_2,
        first_name="Gilly",
        last_name="Bob",
        all_emails=["user@email.gov.uk"],
        is_active=True,
    )
    # Create a user without a profile
    user = user_services.create(sso_email_id=id_3, is_active=True)

    with pytest.raises(Profile.DoesNotExist):
        services.get_profile_by_id(
            id=user.sso_email_id,
            include_inactive=True,
        )

    mock_delete_identity = mocker.patch(
        "core.services.delete_identity", return_value=None
    )
    mock_delete_user = mocker.patch(
        "user.services.delete_from_database", return_value=None
    )

    sso_users = [
        {
            SSO_USER_EMAIL_ID: "sso_user2@gov.uk",
            SSO_FIRST_NAME: "Gilly",
            SSO_LAST_NAME: "Bob",
            SSO_USER_STATUS: "inactive",
            SSO_EMAIL_ADDRESSES: ["sso_user2@gov.uk"],
            SSO_CONTACT_EMAIL_ADDRESS: "user2@gov.uk",
        },
    ]

    profile1_to_delete = services.get_profile_by_id(
        "sso_email_id@email.com", include_inactive=True
    )
    profile2_to_delete = services.get_profile_by_id(id, include_inactive=True)
    calls = [call(profile=profile1_to_delete), call(profile=profile2_to_delete)]

    services.bulk_delete_identity_users_from_sso(sso_users=sso_users)

    mock_delete_identity.assert_has_calls(calls)

    # Delete user without profile via bulk delete
    mock_delete_user.assert_called_once_with(
        user=user,
        reason="Bulk delete - SSO profile does not exist",
    )


def test_bulk_create_and_update_identity_users_from_sso() -> None:
    services.create_identity(
        id="sso_user2@gov.uk",
        first_name="Gilly",
        last_name="Bob",
        all_emails=["user@email.gov.uk"],
        is_active=True,
    )

    sso_users = [
        {
            SSO_USER_EMAIL_ID: "sso_user2@gov.uk",
            SSO_FIRST_NAME: "Jane",
            SSO_LAST_NAME: "Doe",
            SSO_USER_STATUS: "active",
            SSO_EMAIL_ADDRESSES: ["sso_user2@gov.uk"],
            SSO_CONTACT_EMAIL_ADDRESS: "user2@gov.uk",
        },
        {
            SSO_USER_EMAIL_ID: "sso_user3@gov.uk",
            SSO_FIRST_NAME: "Alice",
            SSO_LAST_NAME: "Smith",
            SSO_USER_STATUS: "inactive",
            SSO_EMAIL_ADDRESSES: ["sso_user3@gov.uk"],
            SSO_CONTACT_EMAIL_ADDRESS: "user3@gov.uk",
        },
    ]
    services.bulk_create_and_update_identity_users_from_sso(sso_users=sso_users)
    # mock_create_identity.assert_called_once_with(
    #     id="sso_user3@gov.uk",
    #     first_name="Alice",
    #     last_name="Smith",
    #     all_emails=["sso_user3@gov.uk", "user3@gov.uk"],
    #     is_active=False,
    #     primary_email="sso_user3@gov.uk",
    #     contact_email="user3@gov.uk",
    # )

    # mock_update_identity.assert_called_once_with(
    #     profile=services.get_profile_by_id(
    #         id="sso_user2@gov.uk", include_inactive=True
    #     ),
    #     first_name="Jane",
    #     last_name="Doe",
    #     all_emails=["sso_user2@gov.uk", "user2@gov.uk"],
    #     is_active=True,
    #     primary_email="sso_user2@gov.uk",
    #     contact_email="user2@gov.uk",
    # )


def test_bulk_create_and_update_identity_user_from_sso_without_profile(mocker) -> None:
    # Create a user without a profile
    user = user_services.create(sso_email_id="sso_user@gov.uk", is_active=True)

    with pytest.raises(Profile.DoesNotExist):
        services.get_profile_by_id(
            id=user.sso_email_id,
            include_inactive=True,
        )
    sso_users = [
        {
            SSO_USER_EMAIL_ID: "sso_user@gov.uk",
            SSO_FIRST_NAME: "Jane",
            SSO_LAST_NAME: "Doe",
            SSO_USER_STATUS: "inactive",
            SSO_EMAIL_ADDRESSES: ["sso_user@gov.uk"],
            SSO_CONTACT_EMAIL_ADDRESS: "user@gov.uk",
        },
    ]

    assert user.sso_email_id == "sso_user@gov.uk"
    services.bulk_create_and_update_identity_users_from_sso(sso_users=sso_users)

    profile = services.get_profile_by_id(
        id=user.sso_email_id,
        include_inactive=True,
    )
    updated_user = user_services.get_by_id(
        sso_email_id=user.sso_email_id, include_inactive=True
    )
    assert profile.sso_email_id == user.sso_email_id
    assert updated_user.is_active == False
    assert profile.is_active == False


def test_sync_bulk_sso_users(mocker) -> None:
    services.create_identity(
        id="sso_user1@gov.uk",
        first_name="Billy",
        last_name="Bob",
        all_emails=["new_user@email.gov.uk"],
        is_active=True,
    )
    services.create_identity(
        id="sso_user2@gov.uk",
        first_name="Gilly",
        last_name="Bob",
        all_emails=["user@email.gov.uk"],
        is_active=True,
    )

    mock_get_bulk_user_records = mocker.patch(
        "core.services.get_bulk_user_records_from_sso",
        return_value=[
            {
                SSO_USER_EMAIL_ID: "sso_user2@gov.uk",
                SSO_FIRST_NAME: "Gilly",
                SSO_LAST_NAME: "Doe",
                SSO_USER_STATUS: "active",
                SSO_EMAIL_ADDRESSES: ["sso_user2@gov.uk"],
                SSO_CONTACT_EMAIL_ADDRESS: "user2@gov.uk",
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
                SSO_USER_EMAIL_ID: "sso_user2@gov.uk",
                SSO_FIRST_NAME: "Gilly",
                SSO_LAST_NAME: "Doe",
                SSO_USER_STATUS: "active",
                SSO_EMAIL_ADDRESSES: ["sso_user2@gov.uk"],
                SSO_CONTACT_EMAIL_ADDRESS: "user2@gov.uk",
            },
        ]
    )
    mock_bulk_create_and_update.assert_called_once_with(
        sso_users=[
            {
                SSO_USER_EMAIL_ID: "sso_user2@gov.uk",
                SSO_FIRST_NAME: "Gilly",
                SSO_LAST_NAME: "Doe",
                SSO_USER_STATUS: "active",
                SSO_EMAIL_ADDRESSES: ["sso_user2@gov.uk"],
                SSO_CONTACT_EMAIL_ADDRESS: "user2@gov.uk",
            },
        ]
    )

    mock_get_bulk_user_records.assert_called_once()
