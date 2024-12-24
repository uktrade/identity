import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

from core import services as core_services
from user.exceptions import UserExists


class TestCoreService(TestCase):
    User = get_user_model()

    @pytest.mark.django_db
    @pytest.mark.skip()
    def test_create_user(self):
        # User is created
        user = core_services.create_user(
            id="john.sso.email.id@gov.uk",
            first_name="Billy",
            last_name="Joel",
            emails=[{"address": "test@test.com"}],
        )
        self.assertEqual(user.sso_email_id, "john.sso.email.id@gov.uk")
        self.assertEqual(user.is_active, True)

        # User already exists
        with self.assertRaises(UserExists) as ex:
            existing_user = core_services.create_user(
                id="john.sso.email.id@gov.uk",
                first_name="Billy",
                last_name="Joel",
                emails=[{"address": "test@test.com"}],
            )
