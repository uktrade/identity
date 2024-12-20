import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

from user import services as user_service
from user.exceptions import UserIsDeleted


User = get_user_model()


class UserServiceTest(TestCase):

    @pytest.mark.django_db
    def setUp(self):
        # Create a user for use in the tests
        self.user = User.objects.create_user(
            sso_email_id="sso_email_id@email.com",
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )

    @pytest.mark.django_db
    def test_create_user(self):
        kwargs = {
            "is_active": True,
        }

        user, created = user_service.get_or_create_user(
            sso_email_id="sso_email_id_new_user@email.com",
            **kwargs,
        )

        self.assertEqual(user.sso_email_id, "sso_email_id_new_user@email.com")
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_superuser, False)
        self.assertTrue(created)

    @pytest.mark.django_db
    def test_get_user_by_sso_id(self):
        user = user_service.get_user_by_sso_id(self.user.sso_email_id)
        self.assertEqual(user.sso_email_id, "sso_email_id@email.com")
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_superuser, False)

    @pytest.mark.django_db
    def test_update_user(self):
        kwargs = {
            "is_active": True,
            "is_superuser": True,
        }
        updated_user = user_service.update_user(self.user, **kwargs)
        self.assertEqual(updated_user.sso_email_id, "sso_email_id@email.com")
        self.assertEqual(updated_user.is_active, True)
        self.assertEqual(updated_user.is_superuser, True)

    @pytest.mark.django_db
    def test_update_user_user_error(self):
        # check error when unrecognised user field is provided
        with self.assertRaises(ValueError) as te:
            kwargs = {"unrecognised_field": "value"}
            user_service.update_user(self.user, **kwargs)
        self.assertEqual(
            str(te.exception), "unrecognised_field is not a valid field for User model"
        )

    @pytest.mark.django_db
    def test_delete_user(self):
        user_for_deletion = User.objects.create_user(
            sso_email_id="userfordeletion",
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        deleted_user = user_service.delete_user(user_for_deletion.sso_email_id)
        self.assertFalse(deleted_user.is_active)

        # Try to get a soft-deleted user
        with self.assertRaises(UserIsDeleted) as ex:
            user_service.get_user_by_sso_id(user_for_deletion.sso_email_id)
        self.assertEqual(ex.exception.message, "User has been previously deleted")

    @pytest.mark.django_db
    def test_restore_user(self):
        # Soft delete the user first
        deleted_user = user_service.delete_user(self.user.sso_email_id)
        # update the user setting active True
        kwargs = {
            "is_active": True,
        }
        restored_user = user_service.update_user(deleted_user, **kwargs)
        self.assertTrue(restored_user.is_active)

        # Ensure we can access the restored user
        restored_user = user_service.get_user_by_sso_id(restored_user.sso_email_id)
        self.assertEqual(restored_user.sso_email_id, "sso_email_id@email.com")

    @pytest.mark.django_db
    def test_user_not_found(self):
        with self.assertRaises(User.DoesNotExist) as ex:
            user_service.get_user_by_sso_id("9999")
        self.assertEqual(str(ex.exception), "User does not exist")

    @pytest.mark.django_db
    def test_delete_user_errors(self):
        # check if user does not exist
        with self.assertRaises(User.DoesNotExist) as ex:
            user_service.delete_user("9999")
        self.assertEqual(str(ex.exception), "User does not exist")

        # check if user is already deleted
        user_service.delete_user(self.user.sso_email_id)
        with self.assertRaises(UserIsDeleted) as ex:
            user_service.delete_user(self.user.sso_email_id)

        self.assertEqual(ex.exception.message, "User has been previously deleted")
