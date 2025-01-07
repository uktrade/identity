import pytest
from django.test import TestCase

from core import services
from profiles.models.combined import Profile
from profiles.services import staff_sso, update_from_sso
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
            ["new_user@email.gov.uk"],
        )
        sso_profile = staff_sso.get_by_id(profile.sso_email_id)
        print(sso_profile)

        updated_profile = services.update_identity(
            profile.sso_email_id,
            first_name="Joe",
            last_name="Bobby",
            all_emails=["new_user@email.gov.uk"],
            is_active=True,
        )

        self.assertEqual(updated_profile.first_name, "Joe")
        self.assertEqual(updated_profile.last_name, "Bobby")
