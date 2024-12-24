import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

from core import services as core_services
from profiles.models import ProfileTypes
from user.exceptions import UserExists


class TestCoreService(TestCase):
    User = get_user_model()

    @pytest.mark.django_db
    @pytest.mark.skip()
    def test_new_user(self):
        profile_data = {
            "first_name": "Billy",
            "last_name": "Bob",
            "emails": [{}],
        }
        # User is created
        user, created = core_services.new_user(
            id="john.sso.email.id@gov.uk",
            initiator=ProfileTypes.STAFF_SSO.values,  # type: ignore
            profile_data=profile_data,
        )
        self.assertTrue(created)
        self.assertEqual(user.sso_email_id, "john.sso.email.id@gov.uk")
        self.assertEqual(user.is_active, True)

        # User already exists
        with self.assertRaises(UserExists):
            core_services.new_user(
                id="john.sso.email.id@gov.uk",
                initiator=ProfileTypes.STAFF_SSO.values,  # type: ignore
                profile_data=profile_data,
            )
