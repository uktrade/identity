from django.test import TestCase

from core import services
from profiles.models import ProfileTypes
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
            services.new_user(
                sso_email_id,
                ProfileTypes.STAFF_SSO.value,
                profile_data={
                    "first_name": "Billy",
                    "last_name": "Bob",
                    "emails": [{}],
                    "preferred_email": "",
                },
            )

    def test_new_user(self) -> None:
        user = services.new_user(
            "new_user@gov.uk",
            ProfileTypes.STAFF_SSO.value,
            profile_data={
                "first_name": "Billy",
                "last_name": "Bob",
                "emails": [{}],
                "preferred_email": "",
            },
        )
        self.assertTrue(isinstance(user, User))
        self.assertTrue(user.pk)
        self.assertEqual(user.sso_email_id, "new_user@gov.uk")
        self.assertTrue(User.objects.get(sso_email_id="new_user@gov.uk"))

    def test_new_user_with_invalid_initiator(self) -> None:
        with self.assertRaises(ValueError):
            services.new_user(
                "new_user@gov.uk",
                "invalid_initiator",
                profile_data={
                    "first_name": "Billy",
                    "last_name": "Bob",
                    "emails": [{}],
                    "preferred_email": "",
                },
            )
