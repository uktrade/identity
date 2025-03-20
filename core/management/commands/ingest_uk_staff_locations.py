from django.core.management.base import BaseCommand

from core.utils import UkStaffLocationsS3Ingest


class Command(BaseCommand):
    help = "Ingests UK staff locations data."

    def add_arguments(self, parser):
        parser.add_argument("-d", "--dry-run", action="store_true")

    def handle(self, *args, **kwargs):
        dry_run = kwargs["dry_run"]

        UkStaffLocationsS3Ingest()
