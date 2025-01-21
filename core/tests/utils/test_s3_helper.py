from unittest import mock

from django.conf import settings
from django.test import TestCase, override_settings
from django.utils import timezone

from core.utils.s3_helper import (
    cleanup,
    get_file_path,
    get_s3_resource,
    get_sorted_files_in_export_directory,
)


class TestGetS3Resource(TestCase):
    @override_settings(S3_LOCAL_ENDPOINT_URL=None)
    @mock.patch("boto3.resource")
    def test_no_endpoint_url(self, mock_boto3_resource):
        get_s3_resource()

        mock_boto3_resource.assert_called_once_with("s3")

    @override_settings(S3_LOCAL_ENDPOINT_URL="http://localhost:4566")
    @mock.patch("boto3.resource")
    def test_with_endpoint_url(self, mock_boto3_resource):
        get_s3_resource()

        mock_boto3_resource.assert_called_once_with(
            "s3",
            endpoint_url="http://localhost:4566",
            aws_access_key_id="",
            aws_secret_access_key="",
        )


class TestJSONLIngest(TestCase):
    @mock.patch("boto3.resource")
    def test_get_file_path(self, mock_boto3_resource):
        export_directory = "test/"

        self.assertEqual(
            get_file_path(export_directory=export_directory),
            f"{settings.DATA_FLOW_UPLOADS_BUCKET_PATH}/test/",
        )

    @mock.patch("boto3.resource")
    def test_get_sorted_files_in_export_directory_no_files(
        self,
        mock_boto3_resource,
    ):
        export_directory = "test/"

        self.assertEqual(
            get_sorted_files_in_export_directory(export_directory=export_directory), []
        )

    @mock.patch("boto3.resource")
    def test_get_sorted_files_in_export_directory(
        self,
        mock_boto3_resource,
    ):
        file1 = mock.MagicMock(last_modified=timezone.now().isoformat())
        file2 = mock.MagicMock(last_modified=timezone.now().isoformat())
        file3 = mock.MagicMock(last_modified=timezone.now().isoformat())
        mock_boto3_resource.return_value.Bucket.return_value.objects.filter.return_value = [
            file3,
            file2,
            file1,
        ]
        export_directory = "test/"

        self.assertEqual(
            get_sorted_files_in_export_directory(export_directory=export_directory),
            [file1, file2, file3],
        )

    @mock.patch("boto3.resource")
    def test_cleanup(
        self,
        mock_boto3_resource,
    ):
        file1 = mock.MagicMock(last_modified=timezone.now().isoformat())
        file2 = mock.MagicMock(last_modified=timezone.now().isoformat())
        file3 = mock.MagicMock(last_modified=timezone.now().isoformat())
        files = [file1, file2, file3]

        cleanup(files_to_process=files)

        mock_boto3_resource.return_value.Bucket.return_value.delete_objects.assert_called_once_with(
            Delete={
                "Objects": [
                    {"Key": file1.key},
                    {"Key": file2.key},
                ]
            }
        )
