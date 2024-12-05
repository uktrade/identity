import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

from core.schemas.scim_schema import Name, SCIMUser
from core.service import CoreService


class TestCoreService(TestCase):
    core_service = CoreService()
    User = get_user_model()

    @pytest.mark.django_db
    def test_core_get_or_create_user(self):
        scim_user = SCIMUser(
            externalId="john.sso.email.id@gov.uk",
            is_active=True,
            username="john_smith",
            name=Name(
                givenName="John",
                familyName="Smith",
            ),
        )

        # User is created
        user, created = self.core_service.create_user(scim_user)
        self.assertTrue(created)
        self.assertEqual(user.username, "john.sso.email.id@gov.uk")
        self.assertEqual(user.is_active, True)

        # User already exists
        existing_user, is_created = self.core_service.create_user(scim_user)
        self.assertFalse(is_created)

    @pytest.mark.django_db
    def test_get_user(self):

        user = self.User.objects.create_user(
            username="test_user",
            is_active=True,
        )

        user = self.core_service.get_user(user.id)
        self.assertEqual(user.username, "test_user")
        self.assertEqual(user.is_active, True)
