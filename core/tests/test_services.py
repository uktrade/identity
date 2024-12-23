from django.test import TestCase

from core import services
from user.exceptions import UserAlreadyExists
from user.models import User


class TestCreateUser(TestCase):
    def test_existing_user(self):
        # Create test data
        sso_email_id = "test@email.gov.uk"
        User.objects.create_user(
            sso_email_id=sso_email_id,
        )

        with self.assertRaises(UserAlreadyExists):
            services.create_user(sso_email_id)

    def test_new_user(self):
        user = services.create_user("new_user@gov.uk", "not an initiator")
        self.assertTrue(isinstance(user, User))
        self.assertTrue(user.pk)
        self.assertEqual(user.sso_email_id, "new_user@gov.uk")
        self.assertTrue(User.objects.get(sso_email_id="new_user@gov.uk"))

    def test_new_user_with_initiator(self):
        user = services.create_user("new_user@gov.uk")
        self.assertTrue(isinstance(user, User))
        self.assertTrue(user.pk)
        self.assertEqual(user.sso_email_id, "new_user@gov.uk")
        # FIXME: Broken scenario
        assert False
