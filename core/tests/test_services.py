import pytest
from django.test import TestCase

from core import services
from profiles.models.combined import Profile
from user.exceptions import UserExists
from user.models import User


class TestCreateIdentity(TestCase):
    def test_existing_user(self) -> None:
        # Create test data
        sso_email_id = "test@email.gov.uk"
        User.objects.create_user(
            sso_email_id=sso_email_id,
        )

        with self.assertRaises(UserExists):
            services.create_identity(
                sso_email_id,
                "Billy",
                "Bob",
                ["new_user@email.gov.uk"],
            )

    def test_new_user(self) -> None:
        profile = services.create_identity(
            "new_user@gov.uk",
            "Billy",
            "Bob",
            ["new_user@email.gov.uk"],
        )
        self.assertTrue(isinstance(profile, Profile))
        self.assertTrue(profile.pk)
        self.assertEqual(profile.sso_email_id, "new_user@gov.uk")
        self.assertTrue(User.objects.get(sso_email_id="new_user@gov.uk"))


class TestUpdateIdentity(TestCase):
    def test_update_profile(self) -> None:
        profile = services.create_identity(
            "new_user@gov.uk",
            "Billy",
            "Bob",
            [
                {"address": "new_user@email.gov.uk", "type": "", "preferred": False},
            ],
        )
        services.update_identity_profile(profile.sso_email_id, first_name="Joe")
        updated_profile = services.combined.get_by_id(profile.sso_email_id)

        self.assertEqual(updated_profile.first_name, "Joe")
        self.assertEqual(updated_profile.last_name, "Bob")

    def test_update_user(self) -> None:
        sso_email_id = "test@email.gov.uk"
        user = User.objects.create_user(
            sso_email_id=sso_email_id,
        )
        self.assertEqual(user.is_active, True)

        updated_user = services.update_identity_user(user.sso_email_id, is_active=False)

        self.assertEqual(updated_user.is_active, False)
