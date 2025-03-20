from django.core.management.base import BaseCommand

from core.utils import CountriesS3Ingest


class Command(BaseCommand):
    help = "Ingests Countries data."

    def add_arguments(self, parser):
        parser.add_argument("-d", "--dry-run", action="store_true")

    def handle(self, *args, **kwargs):
        dry_run = kwargs["dry_run"]

        CountriesS3Ingest()
