import logging

from data_flow_s3_import.ingest import DataFlowS3Ingest
from profiles.models.generic import Email
from user.models import User


logger = logging.getLogger(__name__)


class StaffSSOUserS3Ingest(DataFlowS3Ingest):
    export_directory = "StaffSSOUsersPipeline/"
    model = User
    model_uses_baseclass = False
    identifier_field = "id"
    mapping = {
        "name": "name",
        "obj_type": "type",
        "first_name": "dit:firstName",  # /PS-IGNORE
        "last_name": "dit:lastName",  # /PS-IGNORE
        "user_id": "dit:StaffSSO:User:userId",
        "status": "dit:StaffSSO:User:status",
        "last_accessed": "dit:StaffSSO:User:lastAccessed",
        "joined": "dit:StaffSSO:User:joined",
        "email_user_id": "dit:StaffSSO:User:emailUserId",
        "contact_email_address": "dit:StaffSSO:User:contactEmailAddress",
        "became_inactive_on": "dit:StaffSSO:User:becameInactiveOn",
    }

    def postprocess_object(self, obj, instance):
        for email in obj["dit:emailAddress"]:
            Email.objects.get_or_create(
                email_address=email,
                staff_sso_user=instance,
            )

    def postprocess_all(self, imported_pks):
        logger.info(
            "DataFlow S3 {self.__class__}: Deleting deleted users %s", imported_pks
        )
        self.get_model_manager().exclude(pk__in=imported_pks).delete()
