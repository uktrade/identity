import pytest
from django.test import TestCase

from profiles.models import TYPES, StaffSSOProfile
from profiles.services.profile import ProfileService
from profiles.services.staff_sso import StaffSSOService
from user.models import User


class ProfileServiceTest(TestCase):

    @pytest.mark.django_db
    def setUp(self):
        self.profile_service = ProfileService()
        self.staff_sso_service = StaffSSOService()

        # Create a user for use in the tests
        self.user, _ = User.objects.get_or_create(
            sso_email_id="email@email.com",
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )

        self.kwargs = {
            "user": self.user,
            "first_name": "John",
            "last_name": "Doe",
        }
        self.emails = [
            {
                "address": "email1@email.com",
                "type": TYPES[0][0],
                "preferred": False,
            },
            {"address": "email2@email.com", "type": TYPES[1][0], "preferred": True},
        ]

    def test_get_or_create_profile(self):
        staff_sso_profile, sso_profile_created = (
            self.staff_sso_service.get_or_create_staff_sso_profile(
                emails=self.emails,
                **self.kwargs,
            )
        )
        profile, profile_created = self.profile_service.get_or_create_profile(
            staff_sso_profile
        )
        self.assertTrue(sso_profile_created)
        self.assertTrue(profile_created)
        self.assertEqual(profile.sso_email_id, "email@email.com")
        self.assertEqual(profile.first_name, "John")
        self.assertEqual(profile.last_name, "Doe")
        self.assertEqual(profile.preferred_email, "email2@email.com")
        self.assertEqual(profile.emails, ["email1@email.com", "email2@email.com"])

    def test_get_profile_by_sso_email_id(self):

        staff_sso_profile, sso_profile_created = (
            self.staff_sso_service.get_or_create_staff_sso_profile(
                emails=self.emails,
                **self.kwargs,
            )
        )
        profile, profile_created = self.profile_service.get_or_create_profile(
            staff_sso_profile
        )
        actual = self.profile_service.get_profile_by_sso_email_id("email@email.com")

        self.assertTrue(sso_profile_created)
        self.assertTrue(profile_created)
        self.assertEqual(actual.sso_email_id, "email@email.com")
        self.assertEqual(actual.first_name, "John")
        self.assertEqual(actual.last_name, "Doe")
        self.assertEqual(actual.preferred_email, "email2@email.com")
        self.assertEqual(actual.emails, ["email1@email.com", "email2@email.com"])
