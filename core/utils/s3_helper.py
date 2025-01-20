import logging

import boto3
from django.conf import settings
from smart_open import open as smart_open


logger = logging.getLogger(__name__)

EXPORT_BUCKET: str = settings.DATA_FLOW_UPLOADS_BUCKET
BUCKET_PATH: str = settings.DATA_FLOW_UPLOADS_BUCKET_PATH


def get_s3_resource():
    if local_endpoint := getattr(settings, "S3_LOCAL_ENDPOINT_URL", None):
        logger.debug("using local S3 endpoint %s", local_endpoint)
        return boto3.resource(
            "s3",
            endpoint_url=local_endpoint,
            aws_access_key_id="",
            aws_secret_access_key="",
        )

    return boto3.resource("s3")


def get_file_path(export_directory: str):
    return f"{BUCKET_PATH}/{export_directory}"


def get_sorted_files_in_export_directory(export_directory: str):
    """
    Get all the files that "could" be ingested and order them by last
    modified date (oldest first)
    """
    bucket = get_s3_resource().Bucket(EXPORT_BUCKET)
    logger.info("ingest_staff_sso_s3: Reading files from bucket %s", bucket)
    files = bucket.objects.filter(
        Prefix=get_file_path(export_directory=export_directory)
    )

    sorted_files = sorted(files, key=lambda x: x.last_modified, reverse=False)

    if len(sorted_files) == 0:
        return []

    return sorted_files


def get_data_to_ingest(export_directory: str):
    # Get all files in the export directory
    files_to_process = get_sorted_files_in_export_directory(export_directory=export_directory)

    if not len(files_to_process):
        return

    # Select the most recent file
    ingest_file = files_to_process[-1]

    ingest_file.source_key = f"s3://{ingest_file.bucket_name}/{ingest_file.key}"

    # Read the file and yield each line
    with smart_open(
        ingest_file.source_key,
        "r",
        transport_params={
            "client": get_s3_resource().meta.client,
        },
        encoding="utf-8",
    ) as file_input_stream:
        logger.info("ingest_staff_sso_s3: Processing file %s", ingest_file.source_key)
        for line in file_input_stream:
            yield line


def cleanup(export_directory: str):
    """
    Delete other files in the export directory
    """
    files_to_process = get_sorted_files_in_export_directory(export_directory=export_directory)

    files_to_delete = files_to_process[:-1]

    delete_keys = [{"Key": file.key} for file in files_to_delete]

    if delete_keys:
        logger.info("ingest_staff_sso_s3: Deleting keys %s", delete_keys)
        bucket = get_s3_resource().Bucket(EXPORT_BUCKET)
        bucket.delete_objects(Delete={"Objects": delete_keys})
