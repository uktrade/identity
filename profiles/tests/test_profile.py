import pytest
from django.test import TestCase

from profiles.models import TYPES
from profiles.services.profile import ProfileService
from profiles.services.staff_sso import StaffSSOService
from user.models import User


class ProfileServiceTest(TestCase):

    @pytest.mark.django_db
    def setUp(self):
        self.profile_service = ProfileService()
        self.staff_sso_service = StaffSSOService()

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

        self.emails = [
            {
                "address": "email1@email.com",
                "type": TYPES[0][0],
                "preferred": False,
            },
            {"address": "email2@email.com", "type": TYPES[1][0], "preferred": True},
        ]

    def test_get_or_create_profile(self):
        staff_sso_profile, sso_profile_created, profile, profile_created = (
            self.create_staff_sso_profile_and_profile()
        )

        self.assertTrue(profile_created)
        self.assertTrue(sso_profile_created)
        self.assertEqual(profile.sso_email_id, "email@email.com")
        self.assertEqual(profile.first_name, "John")
        self.assertEqual(profile.last_name, "Doe")
        self.assertEqual(profile.preferred_email, "email2@email.com")
        self.assertEqual(profile.emails, ["email1@email.com", "email2@email.com"])

    def test_get_profile_by_sso_email_id(self):
        staff_sso_profile, sso_profile_created, profile, profile_created = (
            self.create_staff_sso_profile_and_profile()
        )
        get_profile_result = self.profile_service.get_profile_by_sso_email_id(
            "email@email.com"
        )

        self.assertTrue(sso_profile_created)
        self.assertTrue(profile_created)
        self.assertEqual(get_profile_result.sso_email_id, "email@email.com")
        self.assertEqual(get_profile_result.first_name, "John")
        self.assertEqual(get_profile_result.last_name, "Doe")
        self.assertEqual(get_profile_result.preferred_email, "email2@email.com")
        self.assertEqual(
            get_profile_result.emails, ["email1@email.com", "email2@email.com"]
        )

    @pytest.mark.django_db
    def test_update_profile(self):
        self.create_staff_sso_profile_and_profile()
        kwargs = {
            "first_name": "Tom",
            "last_name": "Jones",
            "preferred_email": "newpref@email.com",
        }
        emails = ["newemail1@email.com", "newemail2@email.com"]
        updated_profile = self.profile_service.update_profile(
            sso_email_id="email@email.com", emails=emails, **kwargs
        )

        self.assertEqual(updated_profile.sso_email_id, "email@email.com")
        self.assertEqual(updated_profile.first_name, "Tom")
        self.assertEqual(updated_profile.last_name, "Jones")
        self.assertEqual(updated_profile.preferred_email, "newpref@email.com")
        self.assertEqual(
            updated_profile.emails, ["newemail1@email.com", "newemail2@email.com"]
        )

    def test_delete_profile(self):
        self.create_staff_sso_profile_and_profile()
        deleted_profile = self.profile_service.delete_profile("email@email.com")

        self.assertEqual(deleted_profile.is_active, False)
        self.assertEqual(deleted_profile.sso_email_id, "email@email.com")
        self.assertEqual(deleted_profile.last_name, "Doe")
        self.assertEqual(deleted_profile.preferred_email, "email2@email.com")
        self.assertEqual(
            deleted_profile.emails, ["email1@email.com", "email2@email.com"]
        )

    def create_staff_sso_profile_and_profile(self):
        staff_sso_profile, sso_profile_created = (
            self.staff_sso_service.get_or_create_staff_sso_profile(
                user=self.user,
                first_name=self.first_name,
                last_name=self.last_name,
                emails=self.emails,
            )
        )
        preferred_email = "email2@email.com"
        emails = [str(email["address"]) for email in self.emails]
        profile, profile_created = self.profile_service.get_or_create_profile(
            sso_email_id=self.sso_email_id,
            first_name=self.first_name,
            last_name=self.last_name,
            preferred_email=preferred_email,
            emails=emails,
        )

        return staff_sso_profile, sso_profile_created, profile, profile_created
