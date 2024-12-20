import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

from scim import services as scim_services
from scim.schemas import SCIMUserIn, SCIMUserOut


class TestSCIMService(TestCase):
    User = get_user_model()

    @pytest.mark.django_db
    def test_scim_get_or_create_user(self):
        scim_user = SCIMUserIn(
            externalId="john.sso.email.id@gov.uk",
            active=True,
        )

        user, created = scim_services.get_or_create_user(scim_user)
        self.assertTrue(created)
        self.assertEqual(user["sso_email_id"], "john.sso.email.id@gov.uk")
        self.assertEqual(user["is_active"], True)

        # User already exists
        existing_user, is_created = scim_services.get_or_create_user(scim_user)
        self.assertFalse(is_created)

    @pytest.mark.django_db
    def test_scim_get_user_by_id(self):

        test_user = self.User.objects.create_user(
            sso_email_id="test_user.email.id@gov.uk",
            is_active=True,
        )

        user = scim_services.get_user_by_id(test_user.sso_email_id)
        self.assertEqual(user["sso_email_id"], "test_user.email.id@gov.uk")
        self.assertEqual(user["is_active"], True)
