import copy
import json
from unittest.mock import call

import boto3
import pytest
from django.conf import settings
from django.test import override_settings

from core.services import create_identity, get_identity_by_id
from core.utils import StaffSSOUserS3Ingest
from core.utils import get_s3_resource as util_s3_resource
from data_flow_s3_import.tests.utils import S3BotoResource
from profiles.models.combined import Profile


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True, scope="function")
def basic_user(): ...


john_smith = {
    "published": "2024-11-06T15:06:57.880Z",
    "object": {
        "id": "dit:StaffSSO:User:1a23b4cd-5e67-8f9d-0gh1-ijkl23mn45op",
        "type": "dit:StaffSSO:User",
        "name": "John Smith",
        "dit:StaffSSO:User:userId": "1a23b4cd-5e67-8f9d-0gh1-ijkl23mn45op",
        "dit:StaffSSO:User:emailUserId": "johnsmith-09876@example.com",
        "dit:StaffSSO:User:contactEmailAddress": "johnsmith@example.com",
        "dit:StaffSSO:User:joined": "2024-11-06T15:06:57.881Z",
        "dit:StaffSSO:User:lastAccessed": "2024-11-06T15:06:57.881Z",
        "dit:StaffSSO:User:permittedApplications": [],
        "dit:StaffSSO:User:status": "active",
        "dit:StaffSSO:User:becameInactiveOn": "2024-11-06T15:06:57.881Z",
        "dit:firstName": "John",
        "dit:lastName": "Smith",
        "dit:emailAddress": ["johnsmith@example.com"],
    },
}
jane_doe = {
    "published": "2024-12-06T15:06:57.880Z",
    "object": {
        "id": "dit:StaffSSO:User:2a23b4cd-5e67-8f9d-0gh1-ijkl23mn45op",
        "type": "dit:StaffSSO:User",
        "name": "Jane Doe",
        "dit:StaffSSO:User:userId": "2a23b4cd-5e67-8f9d-0gh1-ijkl23mn45op",
        "dit:StaffSSO:User:emailUserId": "janedoe-12345@example.com",
        "dit:StaffSSO:User:contactEmailAddress": "janedoe@example.com",
        "dit:StaffSSO:User:joined": "2024-11-06T15:06:57.881Z",
        "dit:StaffSSO:User:lastAccessed": "2024-11-06T15:06:57.881Z",
        "dit:StaffSSO:User:permittedApplications": [],
        "dit:StaffSSO:User:status": "inactive",
        "dit:StaffSSO:User:becameInactiveOn": None,
        "dit:firstName": "Jane",
        "dit:lastName": "Doe",
        "dit:emailAddress": ["janedoe@example.gov"],
    },
}


@pytest.fixture(autouse=False, scope="function")
@override_settings(DATA_FLOW_UPLOADS_BUCKET="identity.local")
@override_settings(DATA_FLOW_UPLOADS_BUCKET_PATH="test-e2e")
@override_settings(DATA_FLOW_USERS_DIRECTORY="users/")
def create_ingest_source_files():
    s3_resource = get_s3_resource()
    # bucket = s3_resource.Bucket(name=settings.DATA_FLOW_UPLOADS_BUCKET)  #  type: ignore
    file_prefix = "test-e2e/users/"

    newest = s3_resource.Object(  #  type: ignore
        bucket_name=settings.DATA_FLOW_UPLOADS_BUCKET, key=f"{file_prefix}newest.jsonl"
    )  #  type:ignore
    newest_content = json.dumps(john_smith)
    newest_content += "\n"
    newest_content += json.dumps(jane_doe)
    newest.put(
        Body=newest_content, Metadata={"last-modified": "2024-11-06T15:06:57.880Z"}
    )

    middle = s3_resource.Object(  #  type: ignore
        bucket_name=settings.DATA_FLOW_UPLOADS_BUCKET, key=f"{file_prefix}middle.jsonl"
    )  #  type:ignore
    middle_content = json.dumps(john_smith)
    middle_content += "\n"
    middle_content += json.dumps(jane_doe)
    middle_content.replace("John", "Brian")
    middle_content.replace(
        "johnsmith-09876@example.com", "briansmith-09876@example.com"
    )
    middle_content.replace("Jane", "Beatrice")
    middle_content.replace("janedoe-12345@example.com", "beatricedoe-12345@example.com")
    middle.put(
        Body=middle_content, Metadata={"last-modified": "2024-11-05T15:06:57.880Z"}
    )

    oldest = s3_resource.Object(  #  type: ignore
        bucket_name=settings.DATA_FLOW_UPLOADS_BUCKET, key=f"{file_prefix}oldest.jsonl"
    )  #  type:ignore
    oldest_content = json.dumps(john_smith)
    oldest_content += "\n"
    oldest_content += json.dumps(jane_doe)
    oldest_content.replace("John", "Adam")
    middle_content.replace(
        "adamsmith-09876@example.com", "briansmith-09876@example.com"
    )
    oldest_content.replace("Jane", "Africa")
    middle_content.replace(
        "africadoe-12345@example.com", "beatricedoe-12345@example.com"
    )
    oldest.put(
        Body=oldest_content, Metadata={"last-modified": "2024-10-06T15:06:57.880Z"}
    )


def get_s3_resource():
    return boto3.resource(
        "s3",
        endpoint_url=settings.S3_LOCAL_ENDPOINT_URL,
        aws_access_key_id="",
        aws_secret_access_key="",
    )


@override_settings(S3_LOCAL_ENDPOINT_URL="http://localhost:4566")
def test_get_s3_resource_with_endpoint(mocker):
    """Test s3 resource creation based on S3_LOCAL_ENDPOINT_URL setting."""

    mock_boto3_resource = mocker.patch("boto3.resource")
    util_s3_resource()

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
    util_s3_resource()

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
@override_settings(DATA_FLOW_UPLOADS_BUCKET="identity.local")
@override_settings(DATA_FLOW_UPLOADS_BUCKET_PATH="test-e2e")
@override_settings(DATA_FLOW_USERS_DIRECTORY="users/")
def test_new_users_are_added(create_ingest_source_files):
    with pytest.raises(Profile.DoesNotExist):
        get_identity_by_id(id="johnsmith-09876@example.com")
    with pytest.raises(Profile.DoesNotExist):
        get_identity_by_id(id="janedoe-12345@example.com")

    StaffSSOUserS3Ingest()

    john = get_identity_by_id(id="johnsmith-09876@example.com", include_inactive=True)
    assert john.first_name == "John"
    assert john.last_name == "Smith"
    assert john.contact_email == "johnsmith@example.com"
    assert john.is_active == True
    assert john.emails == [
        "johnsmith@example.com",
    ]
    jane = get_identity_by_id(id="janedoe-12345@example.com", include_inactive=True)
    assert jane.first_name == "Jane"
    assert jane.last_name == "Doe"
    assert jane.contact_email == "janedoe@example.com"
    assert jane.is_active == False
    assert jane.emails == ["janedoe@example.gov", "janedoe@example.com"]


@pytest.mark.e2e
@override_settings(DATA_FLOW_UPLOADS_BUCKET="identity.local")
@override_settings(DATA_FLOW_UPLOADS_BUCKET_PATH="test-e2e")
@override_settings(DATA_FLOW_USERS_DIRECTORY="users/")
def test_changed_users_are_updated(create_ingest_source_files):
    create_identity(
        id="johnsmith-09876@example.com",
        first_name="Billy",
        last_name="Thornton",
        all_emails=["billy@joel.com"],
        is_active=True,
    )
    create_identity(
        id="janedoe-12345@example.com",
        first_name="Jane",
        last_name="Doe",
        all_emails=["janedoe@example.com"],
        is_active=True,
    )

    StaffSSOUserS3Ingest()

    john = get_identity_by_id(id="johnsmith-09876@example.com", include_inactive=True)
    assert john.first_name == "John"
    assert john.last_name == "Smith"
    assert john.contact_email == "johnsmith@example.com"
    assert john.is_active == True
    assert john.emails == [
        "johnsmith@example.com",
    ]
    jane = get_identity_by_id(id="janedoe-12345@example.com", include_inactive=True)
    assert jane.first_name == "Jane"
    assert jane.last_name == "Doe"
    assert jane.contact_email == "janedoe@example.com"
    assert jane.is_active == False
    assert "janedoe@example.gov" in jane.emails
    assert "janedoe@example.com" in jane.emails
    assert len(jane.emails) == 2


@pytest.mark.e2e
@override_settings(DATA_FLOW_UPLOADS_BUCKET="identity.local")
@override_settings(DATA_FLOW_UPLOADS_BUCKET_PATH="test-e2e")
@override_settings(DATA_FLOW_USERS_DIRECTORY="users/")
def test_missing_users_are_deleted(create_ingest_source_files):
    create_identity(
        id="billy@example.com",
        first_name="Billy",
        last_name="Thornton",
        all_emails=["billy@joel.com"],
        is_active=True,
    )
    create_identity(
        id="Janet@example.com",
        first_name="Janet",
        last_name="Doe",
        all_emails=["janetdoe@example.com"],
        is_active=True,
    )
    assert Profile.objects.count() == 2
    get_identity_by_id(id="billy@example.com", include_inactive=True)
    get_identity_by_id(id="Janet@example.com", include_inactive=True)

    StaffSSOUserS3Ingest()

    assert Profile.objects.count() == 2
    with pytest.raises(Profile.DoesNotExist):
        get_identity_by_id(id="billy@example.com", include_inactive=True)
    with pytest.raises(Profile.DoesNotExist):
        get_identity_by_id(id="Janet@example.com", include_inactive=True)
    get_identity_by_id(id="johnsmith-09876@example.com", include_inactive=True)
    get_identity_by_id(id="janedoe-12345@example.com", include_inactive=True)
