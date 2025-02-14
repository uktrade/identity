import copy
import pytest
from unittest.mock import call

from django.test import override_settings

from core.utils import StaffSSOUserS3Ingest, get_s3_resource
from data_flow_s3_import.ingest import S3BotoResource
from profiles.models.combined import Profile


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


def test_process_all(mocker):
    mocker.patch(
        "core.utils.StaffSSOUserS3Ingest._get_files_to_ingest",
        return_value=None,
    )
    mock_get_data = mocker.patch(
        "core.utils.StaffSSOUserS3Ingest._get_data_to_ingest",
        return_value=[1, 2, 3, 4],
    )
    mock_process_row = mocker.patch(
        "core.utils.StaffSSOUserS3Ingest.process_row", return_value="__pk__"
    )
    mock_delete = mocker.patch(
        "core.utils.StaffSSOUserS3Ingest.delete_unimported_profiles"
    )
    dfs = StaffSSOUserS3Ingest(s3_resource=S3BotoResource(), bucket_name="bucket_name")
    dfs.process_all()

    mock_get_data.assert_called_once_with()
    assert mock_process_row.call_count == 4
    mock_delete.assert_called_once_with(
        imported_pks=["__pk__", "__pk__", "__pk__", "__pk__"]
    )


def test_process_object(mocker):
    mocker.patch(
        "core.utils.StaffSSOUserS3Ingest._get_files_to_ingest",
        return_value=None,
    )
    mock_emails = mocker.patch(
        "core.utils.StaffSSOUserS3Ingest.extract_emails_from_sso_user",
        return_value=("one@eg.gov", "two@eg.gov.uk", ["three@eg.gov.uk"]),
    )
    mock_svc_get = mocker.patch(
        "core.utils.get_identity_by_id", return_value="--profile--"
    )
    mock_svc_create = mocker.patch("core.utils.create_identity")
    mock_svc_update = mocker.patch("core.utils.update_identity")
    dfs = StaffSSOUserS3Ingest(s3_resource=S3BotoResource(), bucket_name="bucket_name")
    valid_obj = {
        "dit:StaffSSO:User:emailUserId": "12345@example.gov.uk",
        "dit:firstName": "Joe",
        "dit:lastName": "Bloggs",
        "dit:emailAddress": ["joe@example.gov.uk"],
        "dit:StaffSSO:User:contactEmailAddress": "bloggs.j@example.com",
        "dit:StaffSSO:User:status": "active",
    }

    obj = copy.deepcopy(valid_obj)
    del obj["dit:StaffSSO:User:emailUserId"]
    with pytest.raises(KeyError):
        dfs.process_object(obj=obj)

    obj = copy.deepcopy(valid_obj)
    ret = dfs.process_object(obj=obj)
    assert ret == "12345@example.gov.uk"
    mock_emails.assert_called_once_with(obj=obj)
    mock_svc_get.assert_called_once_with(
        id="12345@example.gov.uk", include_inactive=True
    )
    mock_svc_create.assert_not_called()
    mock_svc_update.assert_called_once_with(
        profile="--profile--",
        first_name="Joe",
        last_name="Bloggs",
        all_emails=["three@eg.gov.uk"],
        is_active=True,
        primary_email="one@eg.gov",
        contact_email="two@eg.gov.uk",
    )

    obj = copy.deepcopy(valid_obj)
    del obj["dit:lastName"]
    with pytest.raises(KeyError):
        dfs.process_object(obj=obj)

    obj = copy.deepcopy(valid_obj)
    mock_svc_update.reset_mock()
    mock_svc_create.reset_mock()
    mock_svc_get.side_effect = Profile.DoesNotExist

    ret = dfs.process_object(obj=obj)
    mock_svc_create.assert_called_once_with(
        id="12345@example.gov.uk",
        first_name="Joe",
        last_name="Bloggs",
        all_emails=["three@eg.gov.uk"],
        is_active=True,
        primary_email="one@eg.gov",
        contact_email="two@eg.gov.uk",
    )
    mock_svc_update.assert_not_called()

    obj["dit:StaffSSO:User:status"] = "inactive"
    mock_svc_create.reset_mock()
    ret = dfs.process_object(obj=obj)
    mock_svc_create.assert_called_once_with(
        id="12345@example.gov.uk",
        first_name="Joe",
        last_name="Bloggs",
        all_emails=["three@eg.gov.uk"],
        is_active=False,
        primary_email="one@eg.gov",
        contact_email="two@eg.gov.uk",
    )


def test_extract_emails_from_sso_user(mocker):
    mocker.patch(
        "core.utils.StaffSSOUserS3Ingest._get_files_to_ingest",
        return_value=None,
    )
    dfs = StaffSSOUserS3Ingest(s3_resource=S3BotoResource(), bucket_name="bucket_name")
    valid_obj = {
        "dit:StaffSSO:User:emailUserId": "12345@example.gov.uk",
        "dit:firstName": "Joe",
        "dit:lastName": "Bloggs",
        "dit:emailAddress": ["joe@example.gov.uk", "another@email.tld"],
        "dit:StaffSSO:User:contactEmailAddress": "bloggs.j@example.com",
        "dit:StaffSSO:User:status": "active",
    }

    obj = copy.deepcopy(valid_obj)
    del obj["dit:emailAddress"]
    with pytest.raises(KeyError):
        dfs.extract_emails_from_sso_user(obj)

    obj = copy.deepcopy(valid_obj)
    del obj["dit:StaffSSO:User:contactEmailAddress"]
    with pytest.raises(KeyError):
        dfs.extract_emails_from_sso_user(obj)

    obj = copy.deepcopy(valid_obj)
    ret = dfs.extract_emails_from_sso_user(obj)
    assert ret == (
        "joe@example.gov.uk",
        "bloggs.j@example.com",
        [
            "joe@example.gov.uk",
            "another@email.tld",
            "bloggs.j@example.com",
        ],
    )


def test_delete_unimported_profiles(mocker):
    mocker.patch(
        "core.utils.StaffSSOUserS3Ingest._get_files_to_ingest",
        return_value=None,
    )
    mock_user_qs = mocker.Mock()
    mock_user = mocker.patch("core.utils.User")  # mocker.Mock()
    mock_user.objects.exclude.return_value = mock_user_qs
    mock_user_qs.values_list.return_value = [55, 66, 77, 88]
    # mocker.patch("django.contrib.auth.get_user_model", return_value=mock_user)
    mock_svc_delete = mocker.patch("core.utils.delete_identity")
    mock_svc_get = mocker.patch(
        "core.utils.get_identity_by_id", return_value="--profile--"
    )
    dfs = StaffSSOUserS3Ingest(s3_resource=S3BotoResource(), bucket_name="bucket_name")

    dfs.delete_unimported_profiles(imported_pks=[543, 654, 765])
    mock_user.objects.exclude.assert_called_once_with(sso_email_id__in=[543, 654, 765])
    mock_svc_get.assert_has_calls(
        [
            call(id=55, include_inactive=True),
            call(id=66, include_inactive=True),
            call(id=77, include_inactive=True),
            call(id=88, include_inactive=True),
        ]
    )
    mock_svc_delete.assert_has_calls(
        [
            call(profile="--profile--"),
            call(profile="--profile--"),
            call(profile="--profile--"),
            call(profile="--profile--"),
        ]
    )
    assert mock_svc_delete.call_count == 4


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
