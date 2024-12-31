import pytest
from django.test import TestCase

from core import services
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
                [
                    {
                        "address": "new_user@email.gov.uk",
                        "type": "",
                        "preferred": False,
                    },
                ],
            )

    # FIXME: After we implement "generate_combined_profile_data(sso_email_id)
    # update the test and the expected failure.
    @pytest.mark.xfail(raises=NotImplementedError)
    def test_new_user(self) -> None:
        user = services.create_identity(
            "new_user@gov.uk",
            "Billy",
            "Bob",
            [
                {"address": "new_user@email.gov.uk", "type": "", "preferred": False},
            ],
        )
        self.assertTrue(isinstance(user, User))
        self.assertTrue(user.pk)
        self.assertEqual(user.sso_email_id, "new_user@gov.uk")
        self.assertTrue(User.objects.get(sso_email_id="new_user@gov.uk"))
