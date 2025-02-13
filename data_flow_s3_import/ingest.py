import json
import logging
from typing import Any, Iterable, Iterator

from django.db.models import Model
from django.db.models.manager import BaseManager
from smart_open import open as smart_open


logger = logging.getLogger(__name__)

PrimaryKey = Any
S3Bucket = Any
S3ObjectSummary = Any


class S3BotoResource:
    class meta:
        class client: ...

    class Bucket[S3Bucket]:
        def __init__(self, name: str):
            self.name = name


class DataFlowS3Ingest:
    export_bucket: str
    export_path: str
    export_directory: str
    delete_after_import: bool = True

    def __init__(
        self, s3_resource: S3BotoResource | None = None, bucket_name: str | None = None
    ) -> None:
        self.s3_resource: S3BotoResource = s3_resource or self.get_s3_resource()
        self.export_bucket = bucket_name or self.get_export_bucket_name()
        self.bucket: S3Bucket = self.s3_resource.Bucket(self.export_bucket)
        self.ingest_file: S3ObjectSummary | None = None
        self.other_files: list[S3ObjectSummary] = []

        return self._process_all_workflow()

    def get_s3_resource(self) -> S3BotoResource:
        """
        Hook for boto resource initialiser. Not required if object is initialised with resource.
        """
        raise NotImplementedError()

    def get_export_bucket_name(self) -> str:
        """
        Get the bucket name if not set on the subclass attribute.
        """
        raise NotImplementedError()

    def get_export_path(self) -> str:
        """
        Get the bucket key prefix from the combination of env config and imported data type string
        """
        return f"{self.export_path}/{self.export_directory}"

    def preprocess_all(self) -> None:
        """
        A hook for pre-processing required before any rows in the active file are sent for processing.
        """
        ...

    def process_all(self):
        data: Iterator[str] | None = self._get_data_to_ingest()

        if data is None:
            logger.info(f"DataFlow S3 {self.__class__}: No data found to ingest")
            return

        for item in data:
            self.process_row(line=item)

    def postprocess_all(self) -> None:
        """
        A hook for any post-processing required after all row by processing is completed
        """
        ...

    def process_row(self, line: str) -> PrimaryKey:
        """
        Takes a row of the file, retrieves a dict of the instance it refers to and hands that off for processing
        """
        row: dict = json.loads(s=line)
        obj: dict = row["object"]  # standard for the Data Flow structure
        return self._process_object_workflow(obj=obj)

    def preprocess_object(self, obj: dict) -> None:
        """
        A hook for any pre-processing required before the main object is written to the DB
        """
        ...

    def process_object(self, obj: dict, **kwargs):
        raise NotImplementedError()

    def postprocess_object(self, obj: dict, **kwargs) -> None:
        """
        A hook for any post-processing required after the main object is written to the DB
        """
        ...

    def _process_all_workflow(self) -> None:
        logger.info(f"DataFlow S3 {self.__class__}: Starting S3 ingest")

        if not self._get_files_to_ingest():
            logger.info(f"DataFlow S3 {self.__class__}: No files to ingest")
            return

        self.preprocess_all()

        self.process_all()

        self.postprocess_all()

        self._cleanup()

    def _process_object_workflow(self, obj: dict) -> None:
        """
        Takes a dict referring to a single model instance and saves that instance to the DB using the model manager method.
        """
        self.preprocess_object(obj=obj)

        self.process_object(obj=obj)

        self.postprocess_object(obj=obj)

    def _get_files_to_ingest(self) -> list:
        """
        Get all the files that "could" be ingested and order them by last
        modified date (oldest first)
        """
        logger.info(
            f"DataFlow S3 {self.__class__}: Reading files from bucket {self.bucket}"
        )
        files: Iterable[S3ObjectSummary] = self.bucket.objects.filter(
            Prefix=self.get_export_path()
        )

        sorted_files: list[S3ObjectSummary] = sorted(
            files, key=lambda x: x.last_modified, reverse=False
        )
        for file in sorted_files:
            file.source_key = f"s3://{file.bucket_name}/{file.key}"
            logger.info(
                f"DataFlow S3 {self.__class__}: Found S3 file with key {file.source_key}"
            )

        if len(sorted_files) == 0:
            return []

        return sorted_files

    def _get_data_to_ingest(self) -> Iterator[str]:
        """Yields row by row from the most recent ingestable file"""
        # Get all files in the export directory
        files_to_process = self._get_files_to_ingest()

        if not len(files_to_process):
            return

        # Select the most recent file
        self.ingest_file = files_to_process[-1]
        self.other_files = files_to_process[:-1]

        # Read the file and yield each line
        with smart_open(
            self.ingest_file.source_key,
            "r",
            transport_params={
                "client": self.s3_resource.meta.client,
            },
            encoding="utf-8",
        ) as file_input_stream:
            logger.info(
                f"DataFlow S3 {self.__class__}: Processing file {self.ingest_file.source_key}"
            )
            for line in file_input_stream:
                yield line

    def _cleanup(self) -> None:
        """
        Delete ingested file and other files in the export directory
        """
        files_to_delete = []

        if self.ingest_file:
            files_to_delete.append(self.ingest_file)
        if self.other_files:
            files_to_delete.extend(self.other_files)

        delete_keys = [{"Key": file.key} for file in files_to_delete]

        if delete_keys and not self.delete_after_import:
            logger.info(
                f"DataFlow S3 {self.__class__}: NOT Deleting keys {delete_keys}"
            )
            return

        if delete_keys:
            logger.info(f"DataFlow S3 {self.__class__}: Deleting keys {delete_keys}")
            self.bucket.delete_objects(Delete={"Objects": delete_keys})


class DataFlowS3IngestToModel(DataFlowS3Ingest):
    model: Model.__class__
    model_uses_baseclass: bool = True
    identifier_field: str
    mapping: dict[str, str]

    def __init__(self) -> None:
        self.imported_pks: list[int] = []
        super().__init__()

    def get_model(self) -> Model.__class__:
        """Get model object to create for each row"""
        return self.model

    def get_model_manager(self) -> BaseManager[Model]:
        """Get manager to use for Django data creation methods"""
        return self.get_model().objects

    def process_all(self):
        self.imported_pks = []
        for item in self._get_data_to_ingest():
            created_updated_pk: PrimaryKey = self.process_row(item)
            self.imported_pks.append(created_updated_pk)

    def process_object(self, obj: dict, **kwargs) -> PrimaryKey:
        """
        Takes a dict referring to a single model instance and saves that instance to the DB using the model manager method.
        """
        defaults = {key: obj[value] for key, value in self.mapping.items()}

        if self.model_uses_baseclass:
            defaults["exists_in_last_import"] = True

        (
            instance,
            _,
        ) = self.get_model_manager().update_or_create(
            identifier=obj[self.identifier_field],
            defaults=defaults,
        )

        logger.info(
            f"DataFlow S3 {self.__class__}: Added {self.model} record for {instance.pk}"
        )
        return instance.pk

    def _cleanup(self) -> None:
        if self.model_uses_baseclass:
            self.mark_deleted_upstream()

        return super()._cleanup()

    def mark_deleted_upstream(self) -> None:
        """Mark the objects that are no longer in the S3 file."""
        logger.info(
            f"DataFlow S3 {self.__class__}: Marking models deleted upstream {self.imported_pks}"
        )
        self.get_model_manager().exclude(pk__in=self.imported_pks).update(
            exists_in_last_import=False
        )
