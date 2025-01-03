import pytest
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.test import TestCase

from user import services as user_services
from user.exceptions import UserIsArchived


User = get_user_model()


class TestUserService:
    # @pytest.fixture(autouse=True)
    # def __inject_fixtures(self, mocker):
    #     self.mocker = mocker

    @pytest.mark.django_db
    @pytest.fixture(autouse=True)
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
        user = user_services.get_by_id(self.user.sso_email_id)
        assert user.sso_email_id == "sso_email_id@email.com"
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    @pytest.mark.django_db
    def test_create_user(self):
        assert LogEntry.objects.count() == 0
        user = user_services.create(sso_email_id="sso_email_id_new_user@email.com")

        assert user.sso_email_id == "sso_email_id_new_user@email.com"
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

        assert LogEntry.objects.count() == 1
        log = LogEntry.objects.first()
        assert log.is_addition()
        assert log.user.pk == "via-api"
        assert log.object_repr == str(user)
        assert log.get_change_message() == "Creating new User record"

    @pytest.mark.django_db
    def test_update_user(self):
        LogEntry.objects.all().delete()
        user_services.update(self.user, is_staff=True, is_superuser=True)
        self.user.refresh_from_db()
        assert self.user.sso_email_id == "sso_email_id@email.com"
        assert self.user.is_staff
        assert self.user.is_superuser

        assert LogEntry.objects.count() == 1
        log = LogEntry.objects.first()
        assert log.is_change()
        assert log.user.pk == "via-api"
        assert log.object_repr == str(self.user)
        assert (
            log.get_change_message() == "Updating User record: is_staff, is_superuser"
        )

    @pytest.mark.django_db
    def test_archive(self):
        LogEntry.objects.all().delete()
        user_for_deletion = User.objects.create_user(
            sso_email_id="userfordeletion",
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        user_services.archive(user_for_deletion)
        user_for_deletion.refresh_from_db()
        assert not user_for_deletion.is_active

        # Try to get a soft-deleted user
        with pytest.raises(UserIsArchived) as ex:
            user_services.get_by_id(user_for_deletion.sso_email_id)
            assert ex.value.args[0] == "User has been previously deleted"

        assert LogEntry.objects.count() == 1
        log = LogEntry.objects.first()
        assert log.is_change()
        assert log.user.pk, "via-api"
        assert log.object_repr, str(user_for_deletion)
        assert log.get_change_message() == "Archiving User record"

    @pytest.mark.django_db
    def test_unarchive(self):
        # Soft delete the user first
        user_services.archive(self.user)
        LogEntry.objects.all().delete()
        # update the user setting active True
        user_services.unarchive(self.user)
        self.user.refresh_from_db()
        assert self.user.is_active

        # Ensure we can access the restored user
        restored_user = user_services.get_by_id(self.user.sso_email_id)
        assert restored_user.sso_email_id == "sso_email_id@email.com"

        assert LogEntry.objects.count() == 1
        log = LogEntry.objects.first()
        assert log.is_change()
        assert log.user.pk == "via-api"
        assert log.object_repr == str(self.user)
        assert log.get_change_message() == "Unarchiving User record"

    @pytest.mark.django_db
    def test_delete_from_database(self):
        user_for_deletion = User.objects.create_user(
            sso_email_id="userfordeletion",
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        assert user_services.get_by_id("userfordeletion") == user_for_deletion
        LogEntry.objects.all().delete()
        obj_repr = str(user_for_deletion)
        user_services.delete_from_database(user_for_deletion)
        with pytest.raises(User.DoesNotExist):
            user_services.get_by_id("userfordeletion")

        assert LogEntry.objects.count() == 1
        log = LogEntry.objects.first()
        assert log.is_deletion()
        assert log.user.pk == "via-api"
        assert log.object_repr == obj_repr
        assert log.get_change_message() == "Deleting User record"

    @pytest.mark.django_db
    def test_user_not_found(self):
        with pytest.raises(User.DoesNotExist) as ex:
            user_services.get_by_id("9999")
        assert str(ex.value.args[0]) == "User does not exist"

    @pytest.mark.django_db
    def test_delete_user_errors(self):
        # check if user does not exist
        with pytest.raises(User.DoesNotExist) as ex:
            user_services.archive_by_id("9999")
            assert str(ex.value.args[0]) == "User does not exist"

        # check if user is already deleted
        user_services.archive_by_id(self.user.sso_email_id)
        with pytest.raises(UserIsArchived) as ex:
            user_services.archive_by_id(self.user.sso_email_id)

            assert ex.value.args[0] == "User has been previously deleted"

    @pytest.mark.django_db
    def test_update_by_id(self, mocker):
        self.mocker = mocker
        mock_get_by_id = self.mocker.patch(
            "user.services.get_by_id", return_value=self.user
        )
        mock_update = self.mocker.patch("user.services.update")
        assert not self.user.is_staff
        user_services.update_by_id(self.user.sso_email_id, is_staff=True)
        mock_get_by_id.assert_called_once_with(self.user.sso_email_id)
        mock_update.assert_called_once_with(self.user, True, False)

    @pytest.mark.django_db
    def test_archive_by_id(self, mocker):
        self.mocker = mocker
        mock_get_by_id = self.mocker.patch(
            "user.services.get_by_id", return_value=self.user
        )
        mock_archive = self.mocker.patch("user.services.archive")
        assert self.user.is_active
        user_services.archive_by_id(self.user.sso_email_id)
        mock_get_by_id.assert_called_once_with(self.user.sso_email_id)
        mock_archive.assert_called_once_with(self.user)

    @pytest.mark.django_db
    def test_unarchive_by_id(self, mocker):
        self.mocker = mocker
        mock_get_by_id = self.mocker.patch(
            "user.services.get_by_id", return_value=self.user
        )
        mock_unarchive = self.mocker.patch("user.services.unarchive")
        self.user.is_active = False
        self.user.save()
        assert not self.user.is_active
        user_services.unarchive_by_id(self.user.sso_email_id)
        mock_get_by_id.assert_called_once_with(self.user.sso_email_id)
        mock_unarchive.assert_called_once_with(self.user)

    @pytest.mark.django_db
    def test_delete_from_database_by_id(self, mocker):
        self.mocker = mocker
        mock_get_by_id = self.mocker.patch(
            "user.services.get_by_id", return_value=self.user
        )
        mock_delete_from_database = self.mocker.patch(
            "user.services.delete_from_database"
        )
        assert not self.user.is_staff
        user_services.delete_from_database_by_id(self.user.sso_email_id)
        mock_get_by_id.assert_called_once_with(self.user.sso_email_id)
        mock_delete_from_database.assert_called_once_with(self.user)
