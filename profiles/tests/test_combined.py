import pytest
from django.contrib.admin.models import LogEntry
from django.test import TestCase

from profiles.models.combined import Profile
from profiles.models.generic import EmailObject, EmailTypes
from profiles.services import combined as profile_services
from profiles.services import staff_sso as staff_sso_services
from user.models import User


class CombinedProfileServiceTest(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.sso_email_id = "email@email.com"
        self.first_name = "John"
        self.last_name = "Doe"

        # Create a user for use in the tests
        self.user, _ = User.objects.get_or_create(
            sso_email_id=self.sso_email_id,
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )

        self.emails: list[EmailObject] = [
            {
                "address": "email1@email.com",
                "type": EmailTypes.VERIFIED,
                "preferred": False,
            },
            {
                "address": "email2@email.com",
                "type": EmailTypes.CONTACT,
                "preferred": True,
            },
        ]

    def test_create(self):
        _, profile = self.create_staff_sso_profile_and_profile()

        self.assertEqual(profile.sso_email_id, "email@email.com")
        self.assertEqual(profile.first_name, "John")
        self.assertEqual(profile.last_name, "Doe")
        self.assertEqual(profile.preferred_email, "email2@email.com")
        self.assertEqual(profile.emails, ["email1@email.com", "email2@email.com"])

        self.assertEqual(LogEntry.objects.count(), 1)
        log = LogEntry.objects.first()
        self.assertTrue(log.is_addition())
        self.assertEqual(log.user.pk, "via-api")
        self.assertEqual(log.object_repr, str(profile))
        self.assertEqual(log.get_change_message(), "Creating new Profile")

    def test_get_by_id(self):
        self.create_staff_sso_profile_and_profile()
        get_profile_result = profile_services.get_by_id("email@email.com")

        self.assertEqual(get_profile_result.sso_email_id, "email@email.com")
        self.assertEqual(get_profile_result.first_name, "John")
        self.assertEqual(get_profile_result.last_name, "Doe")
        self.assertEqual(get_profile_result.preferred_email, "email2@email.com")
        self.assertEqual(
            get_profile_result.emails, ["email1@email.com", "email2@email.com"]
        )

    @pytest.mark.django_db
    def test_update(self):
        _, profile = self.create_staff_sso_profile_and_profile()
        emails = ["newemail1@email.com", "newemail2@email.com"]
        LogEntry.objects.first().delete()
        profile_services.update(
            profile,
            first_name="Tom",
            last_name="Jones",
            preferred_email="newpref@email.com",
            emails=emails,
        )

        profile.refresh_from_db()
        self.assertEqual(profile.sso_email_id, "email@email.com")
        self.assertEqual(profile.first_name, "Tom")
        self.assertEqual(profile.last_name, "Jones")
        self.assertEqual(profile.preferred_email, "newpref@email.com")
        self.assertEqual(profile.emails, ["newemail1@email.com", "newemail2@email.com"])

        self.assertEqual(LogEntry.objects.count(), 1)
        log = LogEntry.objects.first()
        self.assertTrue(log.is_change())
        self.assertEqual(log.user.pk, "via-api")
        self.assertEqual(log.object_repr, str(profile))
        self.assertEqual(
            log.get_change_message(),
            "Updating Profile record: first_name, last_name, preferred_email, emails",
        )

    def test_archive(self):
        _, profile = self.create_staff_sso_profile_and_profile()
        LogEntry.objects.all().delete()
        profile_services.archive(profile)

        profile.refresh_from_db()
        self.assertEqual(profile.is_active, False)
        self.assertEqual(profile.sso_email_id, "email@email.com")
        self.assertEqual(profile.last_name, "Doe")
        self.assertEqual(profile.preferred_email, "email2@email.com")
        self.assertEqual(profile.emails, ["email1@email.com", "email2@email.com"])

        self.assertEqual(LogEntry.objects.count(), 1)
        log = LogEntry.objects.first()
        self.assertTrue(log.is_change())
        self.assertEqual(log.user.pk, "via-api")
        self.assertEqual(log.object_repr, str(profile))
        self.assertEqual(
            log.get_change_message(),
            "Archiving Profile record",
        )

    def test_unarchive(self):
        _, profile = self.create_staff_sso_profile_and_profile()
        profile_services.archive(profile)
        profile.refresh_from_db()
        self.assertEqual(profile.is_active, False)
        LogEntry.objects.all().delete()
        profile_services.unarchive(profile)
        profile.refresh_from_db()
        self.assertEqual(profile.is_active, True)
        self.assertEqual(profile.sso_email_id, "email@email.com")

        self.assertEqual(LogEntry.objects.count(), 1)
        log = LogEntry.objects.first()
        self.assertTrue(log.is_change())
        self.assertEqual(log.user.pk, "via-api")
        self.assertEqual(log.object_repr, str(profile))
        self.assertEqual(
            log.get_change_message(),
            "Unarchiving Profile record",
        )

    def test_delete_from_database(self):
        _, profile = self.create_staff_sso_profile_and_profile()
        LogEntry.objects.all().delete()
        obj_repr = str(profile)
        profile.refresh_from_db()
        self.assertEqual(profile.sso_email_id, "email@email.com")
        profile_services.delete_from_database(profile)
        with self.assertRaises(Profile.DoesNotExist):
            profile_services.get_by_id(profile.sso_email_id)

        self.assertEqual(LogEntry.objects.count(), 1)
        log = LogEntry.objects.first()
        self.assertTrue(log.is_deletion())
        self.assertEqual(log.user.pk, "via-api")
        self.assertEqual(log.object_repr, obj_repr)
        self.assertEqual(
            log.get_change_message(),
            "Deleting Profile record",
        )

    def create_staff_sso_profile_and_profile(self):
        self.assertEqual(LogEntry.objects.count(), 0)
        staff_sso_profile = staff_sso_services.create(
            sso_email_id=self.sso_email_id,
            first_name=self.first_name,
            last_name=self.last_name,
            emails=self.emails,
        )
        self.assertEqual(LogEntry.objects.count(), 1)
        LogEntry.objects.first().delete()
        self.assertEqual(LogEntry.objects.count(), 0)
        preferred_email = "email2@email.com"
        emails = [str(email["address"]) for email in self.emails]
        profile = profile_services.create(
            sso_email_id=self.sso_email_id,
            first_name=self.first_name,
            last_name=self.last_name,
            emails=emails,
            preferred_email=preferred_email,
        )

        return staff_sso_profile, profile
