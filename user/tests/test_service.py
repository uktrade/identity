import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

from user import services as user_service
from user.exceptions import UserIsArchived


User = get_user_model()


class UserServiceTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

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
    def test_get_by_id(self):
        user = user_service.get_by_id(self.user.sso_email_id)
        self.assertEqual(user.sso_email_id, "sso_email_id@email.com")
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_superuser, False)

    @pytest.mark.django_db
    def test_create_user(self):
        user = user_service.create(sso_email_id="sso_email_id_new_user@email.com")

        self.assertEqual(user.sso_email_id, "sso_email_id_new_user@email.com")
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_superuser, False)

    @pytest.mark.django_db
    def test_update_user(self):
        kwargs = {
            "is_staff": True,
            "is_superuser": True,
        }
        user_service.update(self.user, **kwargs)
        self.user.refresh_from_db()
        self.assertEqual(self.user.sso_email_id, "sso_email_id@email.com")
        self.assertEqual(self.user.is_staff, True)
        self.assertEqual(self.user.is_superuser, True)

    @pytest.mark.django_db
    def test_archive(self):
        user_for_deletion = User.objects.create_user(
            sso_email_id="userfordeletion",
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        user_service.archive(user_for_deletion)
        user_for_deletion.refresh_from_db()
        self.assertFalse(user_for_deletion.is_active)

        # Try to get a soft-deleted user
        with self.assertRaises(UserIsArchived) as ex:
            user_service.get_by_id(user_for_deletion.sso_email_id)
        self.assertEqual(ex.exception.message, "User has been previously deleted")

    @pytest.mark.django_db
    def test_unarchive(self):
        # Soft delete the user first
        user_service.archive(self.user)
        # update the user setting active True
        user_service.unarchive(self.user)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

        # Ensure we can access the restored user
        restored_user = user_service.get_by_id(self.user.sso_email_id)
        self.assertEqual(restored_user.sso_email_id, "sso_email_id@email.com")

    @pytest.mark.django_db
    def test_delete_from_database(self):
        user_for_deletion = User.objects.create_user(
            sso_email_id="userfordeletion",
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        self.assertEqual(user_service.get_by_id("userfordeletion"), user_for_deletion)
        user_service.delete_from_database(user_for_deletion)
        with self.assertRaises(User.DoesNotExist):
            user_service.get_by_id("userfordeletion")

    @pytest.mark.django_db
    def test_user_not_found(self):
        with self.assertRaises(User.DoesNotExist) as ex:
            user_service.get_by_id("9999")
        self.assertEqual(str(ex.exception), "User does not exist")

    @pytest.mark.django_db
    def test_delete_user_errors(self):
        # check if user does not exist
        with self.assertRaises(User.DoesNotExist) as ex:
            user_service.archive_by_id("9999")
        self.assertEqual(str(ex.exception), "User does not exist")

        # check if user is already deleted
        user_service.archive_by_id(self.user.sso_email_id)
        with self.assertRaises(UserIsArchived) as ex:
            user_service.archive_by_id(self.user.sso_email_id)

        self.assertEqual(ex.exception.message, "User has been previously deleted")

    @pytest.mark.django_db
    def test_update_by_id(self):
        mock_get_by_id = self.mocker.patch(
            "user.services.get_by_id", return_value=self.user
        )
        mock_update = self.mocker.patch("user.services.update")
        self.assertFalse(self.user.is_staff)
        user_service.update_by_id(self.user.sso_email_id, is_staff=True)
        mock_get_by_id.assert_called_once_with(self.user.sso_email_id)
        mock_update.assert_called_once_with(self.user, True, False)

    @pytest.mark.django_db
    def test_archive_by_id(self):
        mock_get_by_id = self.mocker.patch(
            "user.services.get_by_id", return_value=self.user
        )
        mock_archive = self.mocker.patch("user.services.archive")
        self.assertTrue(self.user.is_active)
        user_service.archive_by_id(self.user.sso_email_id)
        mock_get_by_id.assert_called_once_with(self.user.sso_email_id)
        mock_archive.assert_called_once_with(self.user)

    @pytest.mark.django_db
    def test_unarchive_by_id(self):
        mock_get_by_id = self.mocker.patch(
            "user.services.get_by_id", return_value=self.user
        )
        mock_unarchive = self.mocker.patch("user.services.unarchive")
        self.user.is_active = False
        self.user.save()
        self.assertFalse(self.user.is_active)
        user_service.unarchive_by_id(self.user.sso_email_id)
        mock_get_by_id.assert_called_once_with(self.user.sso_email_id)
        mock_unarchive.assert_called_once_with(self.user)

    @pytest.mark.django_db
    def test_delete_from_database_by_id(self):
        mock_get_by_id = self.mocker.patch(
            "user.services.get_by_id", return_value=self.user
        )
        mock_delete_from_database = self.mocker.patch(
            "user.services.delete_from_database"
        )
        self.assertFalse(self.user.is_staff)
        user_service.delete_from_database_by_id(self.user.sso_email_id)
        mock_get_by_id.assert_called_once_with(self.user.sso_email_id)
        mock_delete_from_database.assert_called_once_with(self.user)
