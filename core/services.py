import json
import logging
from typing import Any

from core.utils.s3_helper import (
    cleanup,
    get_data_to_ingest,
    get_sorted_files_in_export_directory,
)
from profiles import services as profile_services
from profiles.models.combined import Profile
from profiles.services import get_all_profiles
from profiles.types import UNSET, Unset  # noqa
from user import services as user_services
from user.models import User


logger = logging.getLogger(__name__)


def get_by_id(id: str):
    return profile_services.get_by_id(sso_email_id=id)


def create_identity(
    id: str,
    first_name: str,
    last_name: str,
    all_emails: list[str],
    primary_email: str | Unset | None = None,
    contact_email: str | Unset | None = None,
) -> Profile:
    """
    Entrypoint for new user creation. Triggers the creation of User record,
    then the relevant Profile record as well as a combined Profile.

    Returns the combined Profile
    """
    user_services.create(sso_email_id=id)
    return profile_services.create_from_sso(
        sso_email_id=id,
        first_name=first_name,
        last_name=last_name,
        all_emails=all_emails,
        contact_email=contact_email,
        primary_email=primary_email,
    )


def update_identity(
    profile: Profile,
    first_name: str,
    last_name: str,
    all_emails: list[str],
    is_active: bool,
    primary_email: str | Unset | None = None,
    contact_email: str | Unset | None = None,
) -> None:
    """
    Function for updating an existing user (archive / unarchive) and their profile information.
    """

    profile_services.update_from_sso(
        profile=profile,
        first_name=first_name,
        last_name=last_name,
        all_emails=all_emails,
        primary_email=primary_email,
        contact_email=contact_email,
    )

    user = User.objects.get(sso_email_id=profile.sso_email_id)
    if user.is_active != is_active:
        if is_active:
            user_services.unarchive(user)
        else:
            user_services.archive(user)


def delete_identity(profile: Profile) -> None:
    """
    Function for deleting an existing user and their profile information.
    """

    profile_services.delete_from_sso(profile=profile)

    # delete user if no profile exists for user
    all_profiles = get_all_profiles(sso_email_id=profile.sso_email_id)
    if not all_profiles:
        user = User.objects.get(sso_email_id=profile.sso_email_id)
        user_services.delete_from_database(user=user)


def get_bulk_user_records_from_sso():
    logger.info("ingest_staff_sso_s3: Starting S3 data read")
    sso_export_directory = "StaffSSOUsersPipeline/"

    sso_users: list[dict] = []
    files = get_sorted_files_in_export_directory(sso_export_directory)
    for item in get_data_to_ingest(files):
        json_item = json.loads(item)
        sso_users.append(json_item["object"])
        logger.info(f"ingest_staff_sso_s3: Added user data for ingestion - {item}")

    logger.info("ingest_staff_sso_s3: Cleaning up unused data files")
    cleanup(files)
    return sso_users


def bulk_delete_identity_users_from_sso(sso_users: list[dict[str, Any]]) -> None:
    """
    Deletes Identity users that are not in the Staff SSO database
    """
    id_users = User.objects.all()
    sso_user_ids = [sso_user["dit:StaffSSO:User:emailUserId"] for sso_user in sso_users]

    id_users_to_delete = id_users.exclude(sso_email_id__in=sso_user_ids)
    for user in id_users_to_delete:
        profile = get_by_id(user.sso_email_id)
        # log Staff SSO objects that are no longer in the S3 file.
        logger.info(f"ingest_staff_sso_s3: Deactivating account {user.sso_email_id}")

        delete_identity(profile=profile)


def bulk_create_and_update_identity_users_from_sso(
    sso_users: list[dict[str, Any]]
) -> None:
    """
    Creates and updates existing Staff SSO users in the Identity database
    """
    id_user_ids = User.objects.all().values_list("sso_email_id", flat=True)

    for sso_user in sso_users:
        if sso_user["dit:StaffSSO:User:status"] == "active":
            if sso_user["dit:StaffSSO:User:emailUserId"] not in id_user_ids:
                primary_email, contact_email, all_emails = extract_emails_from_sso_user(
                    sso_user
                )
                create_identity(
                    id=sso_user["dit:StaffSSO:User:emailUserId"],
                    first_name=sso_user["dit:firstName"],
                    last_name=sso_user["dit:lastName"],
                    all_emails=all_emails,
                    primary_email=primary_email,
                    contact_email=contact_email,
                )
            else:
                profile = get_by_id(id=sso_user["dit:StaffSSO:User:emailUserId"])
                primary_email, contact_email, all_emails = extract_emails_from_sso_user(
                    sso_user
                )
                update_identity(
                    profile=profile,
                    first_name=sso_user["dit:firstName"],
                    last_name=sso_user["dit:lastName"],
                    all_emails=all_emails,
                    is_active=(
                        True
                        if sso_user["dit:StaffSSO:User:status"] == "active"
                        else False
                    ),
                    primary_email=primary_email,
                    contact_email=contact_email,
                )


def extract_emails_from_sso_user(sso_user) -> tuple[str, str, list[str]]:
    primary_email = sso_user["dit:emailAddress"][0]
    contact_email = sso_user["dit:StaffSSO:User:contactEmailAddress"]
    all_emails = sso_user["dit:emailAddress"] + [contact_email]
    return primary_email, contact_email, all_emails


def sync_bulk_sso_users() -> None:
    """
    Retrieves data from the SSO bulk data S3 source and processes it to create, update and delete local ID service Users and related StaffSSOProfile records in bulk.
    """
    sso_users = get_bulk_user_records_from_sso()
    bulk_delete_identity_users_from_sso(sso_users=sso_users)
    bulk_create_and_update_identity_users_from_sso(sso_users=sso_users)
