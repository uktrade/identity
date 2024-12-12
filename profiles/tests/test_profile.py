import pytest
from django.test import TestCase

from profiles.models import TYPES, Email, StaffSSOEmail, StaffSSOProfile
from profiles.services.profile import ProfileService
from user.models import User


class ProfileServiceTest(TestCase):

    @pytest.mark.django_db
    def setUp(self):
        self.profile_service = ProfileService()
        # Create a user for use in the tests
        self.user, _ = User.objects.get_or_create(
            sso_email_id="email@email.com",
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )

        self.profile_request = {
            "user": self.user,
            "first_name": "John",
            "last_name": "Doe",
            "emails": [
                {
                    "address": "email1@email.com",
                    "type": TYPES[0][0],
                    "preferred": False,
                },
                {"address": "email2@email.com", "type": TYPES[1][0], "preferred": True},
            ],
        }

    @pytest.mark.django_db
    def test_get_or_create_staff_sso_profile(self):

        staff_sso_profile, created = (
            self.profile_service.get_or_create_staff_sso_profile(self.profile_request)
        )

        self.assertTrue(created)
        # assert 2 email records created
        self.assertEqual(Email.objects.all().count(), 2)
        self.assertEqual(Email.objects.first().address, "email1@email.com")
        self.assertEqual(Email.objects.last().address, "email2@email.com")

        # assert staff sso profile created
        self.assertEqual(StaffSSOProfile.objects.all().count(), 1)
        self.assertEqual(StaffSSOProfile.objects.first().first_name, "John")
        self.assertEqual(StaffSSOProfile.objects.first().last_name, "Doe")
        self.assertEqual(
            StaffSSOProfile.objects.first().user.sso_email_id, "email@email.com"
        )

        # assert staff sso email created
        self.assertEqual(StaffSSOEmail.objects.all().count(), 2)
        self.assertEqual(
            StaffSSOEmail.objects.first().email.address, "email1@email.com"
        )
        self.assertEqual(StaffSSOEmail.objects.first().type, "work")
        self.assertEqual(StaffSSOEmail.objects.first().preferred, False)
        self.assertEqual(StaffSSOEmail.objects.last().email.address, "email2@email.com")
        self.assertEqual(StaffSSOEmail.objects.last().type, "contact")
        self.assertEqual(StaffSSOEmail.objects.last().preferred, True)
        self.assertEqual(StaffSSOEmail.objects.first().profile.first_name, "John")
        self.assertEqual(StaffSSOEmail.objects.first().profile.last_name, "Doe")
        self.assertEqual(StaffSSOEmail.objects.last().profile.first_name, "John")
        self.assertEqual(StaffSSOEmail.objects.last().profile.last_name, "Doe")

    def test_get_or_create_combined_profile(self):
        staff_sso_profile, sso_profile_created = (
            self.profile_service.get_or_create_staff_sso_profile(self.profile_request)
        )
        combined_profile, combined_profile_created = (
            self.profile_service.get_or_create_combined_profile(staff_sso_profile)
        )
        self.assertTrue(sso_profile_created)
        self.assertTrue(combined_profile_created)
        self.assertEqual(combined_profile.sso_email_id, "email@email.com")
        self.assertEqual(combined_profile.first_name, "John")
        self.assertEqual(combined_profile.last_name, "Doe")
        self.assertEqual(combined_profile.preferred_email, "email2@email.com")
        self.assertEqual(
            combined_profile.emails, ["email1@email.com", "email2@email.com"]
        )

    def test_get_staff_sso_profile_by_id(self):
        staff_sso_profile, created = (
            self.profile_service.get_or_create_staff_sso_profile(self.profile_request)
        )
        actual = self.profile_service.get_staff_sso_profile_by_id(
            str(staff_sso_profile.id)
        )
        self.assertTrue(created)
        self.assertEqual(actual.user.sso_email_id, "email@email.com")
        self.assertEqual(actual.first_name, "John")
        self.assertEqual(actual.last_name, "Doe")

    def test_get_combined_profile_by_sso_email_id(self):

        staff_sso_profile, sso_profile_created = (
            self.profile_service.get_or_create_staff_sso_profile(self.profile_request)
        )
        combined_profile, combined_profile_created = (
            self.profile_service.get_or_create_combined_profile(staff_sso_profile)
        )
        actual = self.profile_service.get_combined_profile_by_sso_email_id(
            "email@email.com"
        )

        self.assertTrue(sso_profile_created)
        self.assertTrue(combined_profile_created)
        self.assertEqual(actual.sso_email_id, "email@email.com")
        self.assertEqual(actual.first_name, "John")
        self.assertEqual(actual.last_name, "Doe")
        self.assertEqual(actual.preferred_email, "email2@email.com")
        self.assertEqual(actual.emails, ["email1@email.com", "email2@email.com"])
