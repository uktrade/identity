import pytest
from django.test import TestCase

from core import services
from profiles.models.combined import Profile
from user.exceptions import UserExists
from user.models import User


class TestCreateUser(TestCase):
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
