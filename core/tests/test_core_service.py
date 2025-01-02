import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

from core import services as core_services
from user.exceptions import UserExists


class TestCoreService(TestCase):
    User = get_user_model()

    @pytest.mark.django_db
    @pytest.mark.skip()
    def test_create_identity(self):
        # User is created
        user = core_services.create_identity(
            id="john.sso.email.id@gov.uk",
            first_name="Billy",
            last_name="Bob",
            emails=[{"address": "test@test.com", "type": None, "preferred": None}],
        )
        self.assertEqual(user.sso_email_id, "john.sso.email.id@gov.uk")
        self.assertEqual(user.is_active, True)

        # User already exists
        with self.assertRaises(UserExists):
            core_services.create_identity(
                id="john.sso.email.id@gov.uk",
                first_name="Billy",
                last_name="Bob",
                emails=[{"address": "test@test.com", "type": None, "preferred": None}],
            )
