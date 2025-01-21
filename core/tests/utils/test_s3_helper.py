from unittest import mock

import pytest
from django.conf import settings
from django.test import override_settings
from django.utils import timezone

from core.utils.s3_helper import (
    cleanup,
    get_file_path,
    get_s3_resource,
    get_sorted_files_in_export_directory,
)


pytestmark = pytest.mark.django_db


def test_get_s3_resource_with_endpoint(mocker, monkeypatch):
    """Test s3 resource creation based on S3_LOCAL_ENDPOINT_URL setting."""
    mock_settings = mocker.patch("core.utils.s3_helper.settings")
    mocker.patch.object(mock_settings, "S3_LOCAL_ENDPOINT_URL", "http://localhost:4566")

    mock_boto3_resource = mocker.patch("boto3.resource")
    get_s3_resource()

    mock_boto3_resource.assert_called_once_with(
        "s3",
        endpoint_url="http://localhost:4566",
        aws_access_key_id="",
        aws_secret_access_key="",
    )


def test_get_s3_resource_no_endpoint(mocker, monkeypatch):
    """Test s3 resource creation based on no S3_LOCAL_ENDPOINT_URL setting."""
    mock_settings = mocker.patch("core.utils.s3_helper.settings")
    mocker.patch.object(mock_settings, "S3_LOCAL_ENDPOINT_URL", None)

    mock_boto3_resource = mocker.patch("boto3.resource")
    get_s3_resource()

    mock_boto3_resource.assert_called_once_with("s3")


@pytest.mark.parametrize(
    "export_directory, expected_path",
    [
        ("test/", f"{settings.DATA_FLOW_UPLOADS_BUCKET_PATH}/test/"),
    ],
)
def test_get_file_path(export_directory, expected_path):
    """Test if get_file_path generates correct file path."""
    assert get_file_path(export_directory=export_directory) == expected_path


@pytest.mark.parametrize(
    "export_directory, mock_files, expected_result",
    [
        ("test/", [], []),
    ],
)
def test_get_sorted_files_in_export_directory_no_files(
    export_directory, mock_files, expected_result, mocker
):
    """Test if get_sorted_files_in_export_directory returns empty list when no files are present."""
    mock_boto3_resource = mocker.patch("boto3.resource")
    mock_boto3_resource.return_value.Bucket.return_value.objects.filter.return_value = (
        mock_files
    )
    assert (
        get_sorted_files_in_export_directory(export_directory=export_directory)
        == expected_result
    )


def test_get_sorted_files_in_export_directory(mocker):
    """Test sorting of files by last modified."""
    mock_boto3_resource = mocker.patch("boto3.resource")

    export_directory = "test/"

    file1 = mock.MagicMock(last_modified=timezone.now().isoformat())
    file2 = mock.MagicMock(last_modified=timezone.now().isoformat())
    file3 = mock.MagicMock(last_modified=timezone.now().isoformat())
    mock_boto3_resource.return_value.Bucket.return_value.objects.filter.return_value = [
        file3,
        file2,
        file1,
    ]
    # mock_boto3_resource.return_value.Bucket.return_value.objects.filter.return_value = mock_files
    assert get_sorted_files_in_export_directory(export_directory=export_directory) == [
        file1,
        file2,
        file3,
    ]


@pytest.mark.parametrize(
    "files_to_process, expected_keys",
    [
        (
            [
                mock.MagicMock(key="file1", last_modified=timezone.now().isoformat()),
                mock.MagicMock(key="file2", last_modified=timezone.now().isoformat()),
                mock.MagicMock(key="file3", last_modified=timezone.now().isoformat()),
            ],
            ["file1", "file2"],
        ),
    ],
)
def test_cleanup(files_to_process, expected_keys, mocker):
    """Test cleanup method which deletes files."""
    mock_boto3_resource = mocker.patch("boto3.resource")

    cleanup(files_to_process=files_to_process)

    mock_boto3_resource.return_value.Bucket.return_value.delete_objects.assert_called_once_with(
        Delete={"Objects": [{"Key": key} for key in expected_keys]}
    )
