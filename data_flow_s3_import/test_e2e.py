import json

import boto3
import pytest
from django.conf import settings
from django.test import override_settings

from data_flow_s3_import.ingest import (
    DataFlowS3Ingest,
    DataFlowS3IngestToModel,
    S3BotoResource,
)
from user.models import User


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.e2e,
]


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
        "dit:StaffSSO:User:status": "active",
        "dit:StaffSSO:User:becameInactiveOn": None,
        "dit:firstName": "Jane",
        "dit:lastName": "Doe",
        "dit:emailAddress": ["janedoe@example.com"],
    },
}


@pytest.fixture(autouse=False, scope="function")
def create_ingest_source_files():
    s3_resource = get_s3_resource()
    # bucket = s3_resource.Bucket(name=settings.DATA_FLOW_UPLOADS_BUCKET)  #  type: ignore
    file_prefix = "test-e2e/users/"

    newest = s3_resource.Object(
        bucket_name=settings.DATA_FLOW_UPLOADS_BUCKET, key=f"{file_prefix}newest.jsonl"
    )  #  type:ignore
    newest_content = json.dumps(john_smith)
    newest_content += "\n"
    newest_content += json.dumps(jane_doe)
    newest.put(
        Body=newest_content, Metadata={"last-modified": "2024-11-06T15:06:57.880Z"}
    )

    middle = s3_resource.Object(
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

    oldest = s3_resource.Object(
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


def test_files_processed_to_python(create_ingest_source_files):
    class TestIngest(DataFlowS3Ingest):
        export_path: str = "test-e2e"
        export_directory = "users/"

        num_objects = 0

        def process_object(self, obj: dict, **kwargs):
            self.num_objects += 1
            assert obj in [john_smith["object"], jane_doe["object"]]
            assert self.num_objects < 3

    s3_resource = get_s3_resource()
    bucket = s3_resource.Bucket(name=settings.DATA_FLOW_UPLOADS_BUCKET)  #  type: ignore
    assert len(list(bucket.objects.filter(Prefix="test-e2e/users/").all())) == 3

    TestIngest(
        s3_resource=s3_resource,  #  type: ignore
        bucket_name=settings.DATA_FLOW_UPLOADS_BUCKET,
    )

    assert len(list(bucket.objects.filter(Prefix="test-e2e/users/").all())) == 0


def test_files_processed_to_django_model_instances(create_ingest_source_files):
    class UserIngest(DataFlowS3IngestToModel):
        export_path: str = "test-e2e"
        export_directory = "users/"
        model = User
        identifier_field_name = "sso_email_id"
        identifier_field_object_mapping = "dit:StaffSSO:User:emailUserId"
        model_uses_baseclass = False
        mapping = {
            "sso_email_id": "dit:StaffSSO:User:emailUserId",
        }

        def _cleanup(self) -> None:
            self.get_model_manager().exclude(pk__in=self.imported_pks).delete()
            return super()._cleanup()

    s3_resource = get_s3_resource()
    bucket = s3_resource.Bucket(name=settings.DATA_FLOW_UPLOADS_BUCKET)  #  type: ignore
    assert len(list(bucket.objects.filter(Prefix="test-e2e/users/").all())) == 3
    assert User.objects.count() == 1
    assert User.objects.all()[0].sso_email_id == "sso_email_id@email.com"

    UserIngest(
        s3_resource=s3_resource,  #  type: ignore
        bucket_name=settings.DATA_FLOW_UPLOADS_BUCKET,
    )

    assert len(list(bucket.objects.filter(Prefix="test-e2e/users/").all())) == 0

    assert User.objects.count() == 2
    assert User.objects.all()[0].sso_email_id == "johnsmith-09876@example.com"
    assert User.objects.all()[1].sso_email_id == "janedoe-12345@example.com"
