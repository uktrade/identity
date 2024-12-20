import pytest
from django.test import TestCase

from profiles.models.generic import EMAIL_TYPE_CONTACT, EMAIL_TYPE_WORK
from profiles.services import combined as profile_service
from profiles.services import staff_sso as staff_sso_service
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

        self.emails = [
            {
                "address": "email1@email.com",
                "type": EMAIL_TYPE_WORK,
                "preferred": False,
            },
            {
                "address": "email2@email.com",
                "type": EMAIL_TYPE_CONTACT,
                "preferred": True,
            },
        ]

    def test_create(self):
        staff_sso_profile, profile = self.create_staff_sso_profile_and_profile()

        self.assertEqual(profile.sso_email_id, "email@email.com")
        self.assertEqual(profile.first_name, "John")
        self.assertEqual(profile.last_name, "Doe")
        self.assertEqual(profile.preferred_email, "email2@email.com")
        self.assertEqual(profile.emails, ["email1@email.com", "email2@email.com"])

    def test_get_by_id(self):
        staff_sso_profile, profile = self.create_staff_sso_profile_and_profile()
        get_profile_result = profile_service.get_by_id("email@email.com")

        self.assertEqual(get_profile_result.sso_email_id, "email@email.com")
        self.assertEqual(get_profile_result.first_name, "John")
        self.assertEqual(get_profile_result.last_name, "Doe")
        self.assertEqual(get_profile_result.preferred_email, "email2@email.com")
        self.assertEqual(
            get_profile_result.emails, ["email1@email.com", "email2@email.com"]
        )

    @pytest.mark.django_db
    def test_update(self):
        sso_profile, profile = self.create_staff_sso_profile_and_profile()
        kwargs = {
            "first_name": "Tom",
            "last_name": "Jones",
            "preferred_email": "newpref@email.com",
        }
        emails = ["newemail1@email.com", "newemail2@email.com"]
        profile_service.update(profile, emails=emails, **kwargs)

        profile.refresh_from_db()
        self.assertEqual(profile.sso_email_id, "email@email.com")
        self.assertEqual(profile.first_name, "Tom")
        self.assertEqual(profile.last_name, "Jones")
        self.assertEqual(profile.preferred_email, "newpref@email.com")
        self.assertEqual(profile.emails, ["newemail1@email.com", "newemail2@email.com"])

    def test_delete(self):
        sso_profile, profile = self.create_staff_sso_profile_and_profile()
        deleted_profile = profile_service.delete(profile)

        profile.refresh_from_db()
        self.assertEqual(profile.is_active, False)
        self.assertEqual(profile.sso_email_id, "email@email.com")
        self.assertEqual(profile.last_name, "Doe")
        self.assertEqual(profile.preferred_email, "email2@email.com")
        self.assertEqual(profile.emails, ["email1@email.com", "email2@email.com"])

    def create_staff_sso_profile_and_profile(self):
        staff_sso_profile = staff_sso_service.create(
            user=self.user,
            first_name=self.first_name,
            last_name=self.last_name,
            emails=self.emails,
        )
        preferred_email = "email2@email.com"
        emails = [str(email["address"]) for email in self.emails]
        profile = profile_service.create(
            sso_email_id=self.sso_email_id,
            first_name=self.first_name,
            last_name=self.last_name,
            preferred_email=preferred_email,
            emails=emails,
        )

        return staff_sso_profile, profile
