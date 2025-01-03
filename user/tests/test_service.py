import pytest
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model

from user import services as user_services
from user.exceptions import UserExists, UserIsArchived, UserIsNotArchived


pytestmark = pytest.mark.django_db

User = get_user_model()


def test_get_by_id(basic_user):
    user = user_services.get_by_id(basic_user.sso_email_id)
    assert user.pk == basic_user.pk

    # Try to get a soft-deleted user
    user.is_active = False
    user.save()
    with pytest.raises(UserIsArchived) as ex:
        user_services.get_by_id(basic_user.sso_email_id)
        assert ex.value.args[0] == "User has been previously deleted"

    # or a non-existent one
    with pytest.raises(User.DoesNotExist) as ex:
        user_services.get_by_id("9999")
        assert str(ex.value.args[0]) == "User does not exist"


def test_create():
    assert LogEntry.objects.count() == 0
    user = user_services.create(
        sso_email_id="sso_email_id_new_user@email.com",
    )

    assert user.sso_email_id == "sso_email_id_new_user@email.com"
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser

    with pytest.raises(UserExists) as ex:
        user_services.create(
            sso_email_id="sso_email_id_new_user@email.com",
        )
        assert str(ex.value.args[0]) == "User has been previously created"

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_addition()
    assert log.user.pk == "via-api"
    assert log.object_repr == str(user)
    assert log.get_change_message() == "Creating new User record"


def test_update(basic_user):
    assert not basic_user.is_staff
    assert not basic_user.is_superuser
    user_services.update(
        basic_user,
        is_staff=True,
        is_superuser=True,
    )
    basic_user.refresh_from_db()
    assert basic_user.sso_email_id == "sso_email_id@email.com"
    assert basic_user.is_staff
    assert basic_user.is_superuser

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_change()
    assert log.user.pk == "via-api"
    assert log.object_repr == str(basic_user)
    assert log.get_change_message() == "Updating User record: is_staff, is_superuser"


def test_archive(basic_user):
    assert basic_user.is_active
    user_services.archive(basic_user)
    basic_user.refresh_from_db()
    assert not basic_user.is_active

    with pytest.raises(UserIsArchived) as ex:
        user_services.archive(basic_user)
        assert str(ex.value.args[0]) == "User is already archived"

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_change()
    assert log.user.pk, "via-api"
    assert log.object_repr, str(basic_user)
    assert log.get_change_message() == "Archiving User record"


def test_unarchive(basic_user):
    basic_user.is_active = False
    basic_user.save()
    basic_user.refresh_from_db()
    assert not basic_user.is_active

    user_services.unarchive(basic_user)
    basic_user.refresh_from_db()
    assert basic_user.is_active

    with pytest.raises(UserIsNotArchived) as ex:
        user_services.unarchive(basic_user)
        assert str(ex.value.args[0]) == "User is not archived"

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_change()
    assert log.user.pk == "via-api"
    assert log.object_repr == str(basic_user)
    assert log.get_change_message() == "Unarchiving User record"


def test_delete_from_database(basic_user):
    id = basic_user.pk
    obj_repr = str(basic_user)
    user_services.delete_from_database(basic_user)
    with pytest.raises(User.DoesNotExist):
        user_services.get_by_id(id)

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_deletion()
    assert log.user.pk == "via-api"
    assert log.object_repr == obj_repr
    assert log.get_change_message() == "Deleting User record"


def test_update_by_id(basic_user, mocker):
    mock_get_by_id = mocker.patch("user.services.get_by_id", return_value=basic_user)
    mock_update = mocker.patch("user.services.update")
    assert not basic_user.is_staff
    user_services.update_by_id(basic_user.sso_email_id, is_staff=True)
    mock_get_by_id.assert_called_once_with(basic_user.sso_email_id)
    mock_update.assert_called_once_with(basic_user, True, False)


def test_archive_by_id(basic_user, mocker):
    mock_get_by_id = mocker.patch("user.services.get_by_id", return_value=basic_user)
    mock_archive = mocker.patch("user.services.archive")
    assert basic_user.is_active
    user_services.archive_by_id(basic_user.sso_email_id)
    mock_get_by_id.assert_called_once_with(basic_user.sso_email_id)
    mock_archive.assert_called_once_with(basic_user)


def test_unarchive_by_id(basic_user, mocker):
    mock_get_by_id = mocker.patch("user.services.get_by_id", return_value=basic_user)
    mock_unarchive = mocker.patch("user.services.unarchive")
    basic_user.is_active = False
    basic_user.save()
    assert not basic_user.is_active
    user_services.unarchive_by_id(basic_user.sso_email_id)
    mock_get_by_id.assert_called_once_with(basic_user.sso_email_id)
    mock_unarchive.assert_called_once_with(basic_user)


def test_delete_from_database_by_id(basic_user, mocker):
    mock_get_by_id = mocker.patch("user.services.get_by_id", return_value=basic_user)
    mock_delete_from_database = mocker.patch("user.services.delete_from_database")
    assert not basic_user.is_staff
    user_services.delete_from_database_by_id(basic_user.sso_email_id)
    mock_get_by_id.assert_called_once_with(basic_user.sso_email_id)
    mock_delete_from_database.assert_called_once_with(basic_user)
