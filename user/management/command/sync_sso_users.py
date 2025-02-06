from django.core.management.base import BaseCommand

from user.utils import StaffSSOUserS3Ingest


class Command(BaseCommand):
    help = (
        "Syncs SSO user data; creating, deleting and updating local users as necessary."
    )

    def add_arguments(self, parser):
        parser.add_argument("-d", "--dry-run", action="store_true")

    def handle(self, *args, **kwargs):
        dry_run = kwargs["dry_run"]

        StaffSSOUserS3Ingest()
