import pytest
from django.test import override_settings

from core.utils import StaffSSOUserS3Ingest, get_s3_resource
from user.models import User


pytestmark = pytest.mark.django_db


@override_settings(S3_LOCAL_ENDPOINT_URL="http://localhost:4566")
def test_get_s3_resource_with_endpoint(mocker):
    """Test s3 resource creation based on S3_LOCAL_ENDPOINT_URL setting."""

    mock_boto3_resource = mocker.patch("boto3.resource")
    get_s3_resource()

    mock_boto3_resource.assert_called_once_with(
        "s3",
        endpoint_url="http://localhost:4566",
        aws_access_key_id="",
        aws_secret_access_key="",
    )


@override_settings(S3_LOCAL_ENDPOINT_URL=None)
def test_get_s3_resource_no_endpoint(mocker):
    """Test s3 resource creation based on no S3_LOCAL_ENDPOINT_URL setting."""

    mock_boto3_resource = mocker.patch("boto3.resource")
    get_s3_resource()

    mock_boto3_resource.assert_called_once_with("s3")


def test_process_all():
    assert False


def test_process_object():
    assert False


def test_extract_emails_from_sso_user():
    assert False


def test_delete_unimported_profiles():
    assert False


@pytest.mark.e2e
def test_new_users_are_added():
    assert False


@pytest.mark.e2e
def test_changed_users_are_updated():
    assert False


@pytest.mark.e2e
def test_missing_users_are_deleted():
    assert False


# @pytest.mark.usefixtures("sso_profile", "combined_profile")
# def test_bulk_delete_identity_users_from_sso(mocker) -> None:
#     id = "sso_user1@gov.uk"
#     services.create_identity(
#         id=id,
#         first_name="Billy",
#         last_name="Bob",
#         all_emails=["new_user@email.gov.uk"],
#         is_active=True,
#     )
#     services.create_identity(
#         id="sso_user2@gov.uk",
#         first_name="Gilly",
#         last_name="Bob",
#         all_emails=["user@email.gov.uk"],
#         is_active=True,
#     )

#     mock_delete_identity = mocker.patch(
#         "core.services.delete_identity", return_value=None
#     )

# sso_users = [
#     {
#         SSO_USER_EMAIL_ID: "sso_user2@gov.uk",
#         SSO_FIRST_NAME: "Gilly",
#         SSO_LAST_NAME: "Bob",
#         SSO_USER_STATUS: "inactive",
#         SSO_EMAIL_ADDRESSES: ["sso_user2@gov.uk"],
#         SSO_CONTACT_EMAIL_ADDRESS: "user2@gov.uk",
#     },
# ]

# profile1_to_delete = services.get_identity_by_id(
#     "sso_email_id@email.com", include_inactive=True
# )
# profile2_to_delete = services.get_identity_by_id(id, include_inactive=True)
# calls = [call(profile=profile1_to_delete), call(profile=profile2_to_delete)]

#     services.bulk_delete_identity_users_from_sso(sso_users=sso_users)

#     mock_delete_identity.assert_has_calls(calls)


# def test_bulk_create_and_update_identity_users_from_sso(mocker) -> None:
#     services.create_identity(
#         id="sso_user2@gov.uk",
#         first_name="Gilly",
#         last_name="Bob",
#         all_emails=["user@email.gov.uk"],
#         is_active=True,
#     )
#     mock_create_identity = mocker.patch(
#         "core.services.create_identity", return_value="__profile__"
#     )
#     mock_update_identity = mocker.patch(
#         "core.services.update_identity", return_value=None
#     )

#     sso_users = [
#         {
#             SSO_USER_EMAIL_ID: "sso_user2@gov.uk",
#             SSO_FIRST_NAME: "Jane",
#             SSO_LAST_NAME: "Doe",
#             SSO_USER_STATUS: "active",
#             SSO_EMAIL_ADDRESSES: ["sso_user2@gov.uk"],
#             SSO_CONTACT_EMAIL_ADDRESS: "user2@gov.uk",
#         },
#         {
#             SSO_USER_EMAIL_ID: "sso_user3@gov.uk",
#             SSO_FIRST_NAME: "Alice",
#             SSO_LAST_NAME: "Smith",
#             SSO_USER_STATUS: "inactive",
#             SSO_EMAIL_ADDRESSES: ["sso_user3@gov.uk"],
#             SSO_CONTACT_EMAIL_ADDRESS: "user3@gov.uk",
#         },
#     ]
#     services.bulk_create_and_update_identity_users_from_sso(sso_users=sso_users)
#     mock_create_identity.assert_called_once_with(
#         id="sso_user3@gov.uk",
#         first_name="Alice",
#         last_name="Smith",
#         all_emails=["sso_user3@gov.uk", "user3@gov.uk"],
#         is_active=False,
#         primary_email="sso_user3@gov.uk",
#         contact_email="user3@gov.uk",
#     )
#     mock_update_identity.assert_called_once_with(
#         profile=services.get_identity_by_id(
#             id="sso_user2@gov.uk", include_inactive=True
#         ),
#         first_name="Jane",
#         last_name="Doe",
#         all_emails=["sso_user2@gov.uk", "user2@gov.uk"],
#         is_active=True,
#         primary_email="sso_user2@gov.uk",
#         contact_email="user2@gov.uk",
#     )


# def test_sync_bulk_sso_users(mocker) -> None:
#     services.create_identity(
#         id="sso_user1@gov.uk",
#         first_name="Billy",
#         last_name="Bob",
#         all_emails=["new_user@email.gov.uk"],
#         is_active=True,
#     )
#     services.create_identity(
#         id="sso_user2@gov.uk",
#         first_name="Gilly",
#         last_name="Bob",
#         all_emails=["user@email.gov.uk"],
#         is_active=True,
#     )

#     mock_get_bulk_user_records = mocker.patch(
#         "core.services.get_bulk_user_records_from_sso",
#         return_value=[
#             {
#                 SSO_USER_EMAIL_ID: "sso_user2@gov.uk",
#                 SSO_FIRST_NAME: "Gilly",
#                 SSO_LAST_NAME: "Doe",
#                 SSO_USER_STATUS: "active",
#                 SSO_EMAIL_ADDRESSES: ["sso_user2@gov.uk"],
#                 SSO_CONTACT_EMAIL_ADDRESS: "user2@gov.uk",
#             },
#         ],
#     )
#     mock_bulk_delete = mocker.patch(
#         "core.services.bulk_delete_identity_users_from_sso", return_value=None
#     )

#     mock_bulk_create_and_update = mocker.patch(
#         "core.services.bulk_create_and_update_identity_users_from_sso",
#         return_value=None,
#     )
#     services.sync_bulk_sso_users()

#     mock_bulk_delete.assert_called_once_with(
#         sso_users=[
#             {
#                 SSO_USER_EMAIL_ID: "sso_user2@gov.uk",
#                 SSO_FIRST_NAME: "Gilly",
#                 SSO_LAST_NAME: "Doe",
#                 SSO_USER_STATUS: "active",
#                 SSO_EMAIL_ADDRESSES: ["sso_user2@gov.uk"],
#                 SSO_CONTACT_EMAIL_ADDRESS: "user2@gov.uk",
#             },
#         ]
#     )
#     mock_bulk_create_and_update.assert_called_once_with(
#         sso_users=[
#             {
#                 SSO_USER_EMAIL_ID: "sso_user2@gov.uk",
#                 SSO_FIRST_NAME: "Gilly",
#                 SSO_LAST_NAME: "Doe",
#                 SSO_USER_STATUS: "active",
#                 SSO_EMAIL_ADDRESSES: ["sso_user2@gov.uk"],
#                 SSO_CONTACT_EMAIL_ADDRESS: "user2@gov.uk",
#             },
#         ]
#     )

#     mock_get_bulk_user_records.assert_called_once()
