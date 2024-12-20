import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

from core import services as core_services
from user.exceptions import UserAlreadyExists


class TestCoreService(TestCase):
    User = get_user_model()

    @pytest.mark.django_db
    @pytest.mark.skip()
    def test_create_user(self):
        user_details = {
            "first_name": "Billy",
        }
        # User is created
        user, created = core_services.create_user(
            id="john.sso.email.id@gov.uk",
            **user_details,
        )
        self.assertTrue(created)
        self.assertEqual(user.sso_email_id, "john.sso.email.id@gov.uk")
        self.assertEqual(user.is_active, True)

        # User already exists
        with self.assertRaises(UserAlreadyExists) as ex:
            existing_user = core_services.create_user(
                id="john.sso.email.id@gov.uk",
                **user_details,
            )
