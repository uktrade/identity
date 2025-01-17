from django.core.management.base import BaseCommand

from core.services import sync_bulk_sso_users


class Command(BaseCommand):
    help = (
        "Syncs SSO user data; creating, deleting and updating local users as necessary."
    )

    def add_arguments(self, parser):
        parser.add_argument("-d", "--dry-run", action="store_true")

    def handle(self, *args, **kwargs):
        dry_run = kwargs["dry_run"]

        sync_bulk_sso_users()
