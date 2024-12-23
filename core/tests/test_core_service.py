import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

from core import services as core_services


class TestCoreService(TestCase):
    User = get_user_model()

    @pytest.mark.django_db
    def test_core_get_or_create_user(self):
        user_details = {
            "is_active": True,
        }
        # User is created
        user, created = core_services.get_or_create_user(
            id="john.sso.email.id@gov.uk",
            **user_details,
        )
        self.assertTrue(created)
        self.assertEqual(user.sso_email_id, "john.sso.email.id@gov.uk")
        self.assertEqual(user.is_active, True)

        # User already exists
        existing_user, is_created = core_services.get_or_create_user(
            id="john.sso.email.id@gov.uk",
            **user_details,
        )
        self.assertFalse(is_created)

    @pytest.mark.django_db
    def test_core_get_user_by_id(self):

        test_user = self.User.objects.create_user(
            sso_email_id="test_user",
            is_active=True,
        )

        user = core_services.get_user_by_id(test_user.sso_email_id)
        self.assertEqual(user.sso_email_id, "test_user")
        self.assertEqual(user.is_active, True)
