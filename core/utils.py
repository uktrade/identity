import json
import logging

import boto3
from data_flow_s3_import import ingest
from data_flow_s3_import.types import PrimaryKey
from django.conf import settings
from django.contrib.auth import get_user_model

from core.services import (
    create_identity,
    delete_identity,
    get_identity_by_id,
    update_identity,
)
from profiles.models.combined import Profile
from profiles.models.generic import Country, SectorList, UkStaffLocation


logger = logging.getLogger(__name__)
User = get_user_model()


def get_s3_resource():
    """Wrapper for boto resource initialiser allowing for local/test"""
    if local_endpoint := getattr(settings, "S3_LOCAL_ENDPOINT_URL", None):
        logger.debug(
            f"DataFlow S3 Import: using local S3 endpoint %s",
            local_endpoint,
        )
        return boto3.resource(
            "s3",
            endpoint_url=local_endpoint,
            aws_access_key_id="",
            aws_secret_access_key="",
        )

    return boto3.resource("s3")


class DataFlowS3Ingest(ingest.DataFlowS3Ingest):
    """
    Set application specific behaviour for DataFlowS3Ingest.
    """

    def get_s3_resource(self):
        return get_s3_resource()


class DataFlowS3IngestToModel(ingest.DataFlowS3IngestToModel):
    """
    Set  application specific behaviour for DataFlowS3IngestToModel.
    """

    def get_s3_resource(self):
        return get_s3_resource()


class StaffSSOUserS3Ingest(DataFlowS3Ingest):
    export_bucket: str = settings.DATA_FLOW_UPLOADS_BUCKET
    export_path: str = settings.DATA_FLOW_UPLOADS_BUCKET_PATH
    export_directory: str = settings.DATA_FLOW_USERS_DIRECTORY

    def process_all(self):
        imported_pks = []
        for item in self._get_data_to_ingest():
            created_updated_pk = self.process_row(line=item)
            imported_pks.append(created_updated_pk)
        self.delete_unimported_profiles(imported_pks=imported_pks)

    def process_object(self, obj, **kwargs):
        sso_email_id = obj["dit:StaffSSO:User:emailUserId"]
        (
            primary_email,
            contact_email,
            all_emails,
        ) = self.extract_emails_from_sso_user(obj=obj)

        try:
            profile: Profile = get_identity_by_id(
                id=sso_email_id, include_inactive=True
            )
        except Profile.DoesNotExist:
            create_identity(
                id=sso_email_id,
                first_name=obj["dit:firstName"],
                last_name=obj["dit:lastName"],
                all_emails=all_emails,
                is_active=obj["dit:StaffSSO:User:status"] == "active",
                primary_email=primary_email,
                contact_email=contact_email,
            )
            logger.info(f"DataFlow S3 {self.__class__}: Created user {sso_email_id}")
        else:
            update_identity(
                profile=profile,
                first_name=obj["dit:firstName"],
                last_name=obj["dit:lastName"],
                all_emails=all_emails,
                is_active=obj["dit:StaffSSO:User:status"] == "active",
                primary_email=primary_email,
                contact_email=contact_email,
            )
            logger.info(f"DataFlow S3 {self.__class__}: Updated user {sso_email_id}")
        return sso_email_id

    def extract_emails_from_sso_user(self, obj) -> tuple[str, str, list[str]]:
        primary_email = obj["dit:emailAddress"][0]
        contact_email = obj["dit:StaffSSO:User:contactEmailAddress"]
        all_emails = obj["dit:emailAddress"] + [contact_email]
        return primary_email, contact_email, all_emails

    def delete_unimported_profiles(self, imported_pks):
        user_ids_to_delete = User.objects.exclude(
            sso_email_id__in=imported_pks
        ).values_list("sso_email_id", flat=True)

        for sso_email_id in user_ids_to_delete:
            profile = get_identity_by_id(id=sso_email_id, include_inactive=True)
            delete_identity(profile=profile)


class CountriesS3Ingest(DataFlowS3IngestToModel):
    export_bucket: str = settings.DATA_FLOW_UPLOADS_BUCKET
    export_path: str = settings.DATA_FLOW_UPLOADS_BUCKET_PATH
    export_directory: str = settings.DATA_FLOW_COUNTRIES_DIRECTORY
    model = Country
    identifier_field_name = "reference_id"
    identifier_field_object_mapping = "reference_id"
    mapping = {
        "reference_id": "reference_id",
        "name": "name",
        "type": "type",
        "iso_1_code": "iso1_code",
        "iso_2_code": "iso2_code",
        "iso_3_code": "iso3_code",
        "overseas_region": "overseas_region",
    }

    def process_row(self, line: str) -> PrimaryKey:
        """
        Takes a row of the file, retrieves a dict of the instance it refers to and hands that off for processing
        """
        obj: dict = json.loads(s=line)  # Countries does not wrap content in 'object'
        return self._process_object_workflow(obj=obj)


class UkStaffLocationsS3Ingest(DataFlowS3IngestToModel):
    export_bucket: str = settings.DATA_FLOW_UPLOADS_BUCKET
    export_path: str = settings.DATA_FLOW_UPLOADS_BUCKET_PATH
    export_directory: str = settings.DATA_FLOW_UK_STAFF_LOCATIONS_DIRECTORY
    model = UkStaffLocation
    identifier_field_name = "code"
    identifier_field_object_mapping = "location_code"
    mapping = {
        "code": "location_code",
        "name": "location_name",
        "city": "city",
        "organisation": "organisation",
        "building_name": "building_name",
    }

    def process_row(self, line: str) -> PrimaryKey:
        """
        Takes a row of the file, retrieves a dict of the instance it refers to and hands that off for processing
        """
        obj: dict = json.loads(
            s=line
        )  # UkStaffLocation does not wrap content in 'object'
        return self._process_object_workflow(obj=obj)


class SectorListS3Ingest(DataFlowS3IngestToModel):
    export_bucket: str = settings.DATA_FLOW_UPLOADS_BUCKET
    export_path: str = settings.DATA_FLOW_UPLOADS_BUCKET_PATH
    export_directory: str = settings.DATA_FLOW_SECTOR_LIST_DIRECTORY
    model = SectorList
    identifier_field_name = "sector_id"
    identifier_field_object_mapping = "field_01"
    mapping = {
        "sector_id": "field_01",
        "full_sector_name": "full_sector_name",
        "sector_cluster_name_april_2023_onwards": "sector_cluster__april_2023",
        "sector_cluster_name_before_april_2023": "field_03",
        "sector_name": "field_04",
        "sub_sector_name": "field_05",
        "sub_sub_sector_name": "field_02",
        "start_date": "field_06",
        "end_date": "field_07",
    }

    def process_row(self, line: str) -> PrimaryKey:
        """
        Takes a row of the file, retrieves a dict of the instance it refers to and hands that off for processing
        """
        obj: dict = json.loads(s=line)  # SectorList does not wrap content in 'object'
        return self._process_object_workflow(obj=obj)
