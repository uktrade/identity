from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandParser
from factory.faker import faker

from core import services
from user import services as user_services


User = get_user_model()


class Command(BaseCommand):
    help = "Creates a local Identity with fixture data"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("-i", "--sso_email_id", type=str)
        parser.add_argument("-e", "--email", type=str)
        parser.add_argument("-f", "--first_name", type=str)
        parser.add_argument("-l", "--last_name", type=str)
        parser.add_argument(
            "-s", "--staff", action="store_true", help="Set user to staff"
        )
        parser.add_argument(
            "-ss", "--superuser", action="store_true", help="Set user to Superuser"
        )
        parser.add_argument("-d", "--dry_run", action="store_true")

    def handle(self, *args, **kwargs):
        sso_email_id = kwargs["sso_email_id"]
        email = kwargs["email"]
        first_name = kwargs["first_name"]
        last_name = kwargs["last_name"]
        staff = kwargs["staff"]
        superuser = kwargs["superuser"]
        is_active = kwargs["is_active"]
        dry_run = kwargs["dry_run"]

        factory_faker = faker.Faker()
        if sso_email_id is None:
            if email is not None:
                sso_email_id = email
            else:
                sso_email_id = factory_faker.email()

        if email is None:
            email = sso_email_id

        if first_name is None:
            first_name = factory_faker.first_name()

        if last_name is None:
            last_name = factory_faker.last_name()

        if is_active is None:
            is_active = factory_faker.is_active()

        self.stdout.write(
            f"Creating user with id: {sso_email_id}, email: {email}, first_name: {first_name} and last_name: {last_name}"
        )
        if dry_run:
            self.stdout.write(msg="This was a dry run, aborting now")
            return

        p = services.create_identity(
            id=sso_email_id,
            first_name=first_name,
            last_name=last_name,
            all_emails=[email],
            is_active=is_active,
        )

        if superuser:
            staff = True

        if staff or superuser:
            self.stdout.write(msg="Setting permissions")
            user_services.update_by_id(
                sso_email_id=p.sso_email_id, is_staff=staff, is_superuser=superuser
            )
            usr = user_services.get_by_id(
                sso_email_id=p.sso_email_id, include_inactive=True
            )
            usr.set_password(sso_email_id)
            usr.save()
            self.stdout.write(msg=f"Password set to '{sso_email_id}'")

        self.stdout.write(msg="Creation complete")
