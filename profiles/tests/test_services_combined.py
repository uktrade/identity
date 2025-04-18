import pytest
from django.contrib.admin.models import LogEntry

from profiles.exceptions import ProfileExists, ProfileIsArchived, ProfileIsNotArchived
from profiles.models.combined import Profile
from profiles.services import combined as profile_services


pytestmark = pytest.mark.django_db


def test_get_by_id(combined_profile):
    # Get an active profile
    get_profile_result = profile_services.get_by_id(combined_profile.sso_email_id)
    assert get_profile_result == combined_profile
    assert combined_profile.is_active == True

    # Get a soft-deleted profile when inactive profiles are included
    combined_profile.is_active = False
    combined_profile.save()

    soft_deleted_profile = profile_services.get_by_id(
        combined_profile.sso_email_id, include_inactive=True
    )
    assert soft_deleted_profile.is_active == False

    # Try to get a soft-deleted profile when inactive profiles are not included
    combined_profile.is_active = False
    combined_profile.save()
    with pytest.raises(Profile.DoesNotExist) as ex:
        # no custom error to keep overheads low
        profile_services.get_by_id(
            combined_profile.sso_email_id,
        )
        assert ex.value.args[0] == "User has been previously deleted"

    # Try to get a non-existent profile
    with pytest.raises(Profile.DoesNotExist) as ex:
        profile_services.get_by_id("9999")
        assert str(ex.value.args[0]) == "User does not exist"


def test_create():
    created_profile = profile_services.create(
        sso_email_id="email@email.com",
        first_name="John",
        last_name="Doe",
        primary_email="email2@email.com",
        all_emails=[
            "email1@email.com",
            "email2@email.com",
        ],
        is_active=True,
    )
    assert created_profile.sso_email_id == "email@email.com"
    assert created_profile.first_name == "John"
    assert created_profile.last_name == "Doe"
    assert created_profile.primary_email == "email2@email.com"
    assert created_profile.emails == ["email1@email.com", "email2@email.com"]

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_addition()
    assert log.user.pk == "via-api"
    assert log.object_repr == str(created_profile)
    assert log.get_change_message() == "Creating new Profile"

    with pytest.raises(ProfileExists) as ex:
        profile_services.create(
            sso_email_id="email@email.com",
            first_name="John",
            last_name="Doe",
            primary_email="email2@email.com",
            all_emails=[
                "email1@email.com",
                "email2@email.com",
            ],
            is_active=True,
        )
        assert str(ex.value.args[0]) == "Profile has been previously created"


def test_update(combined_profile):
    emails = ["newemail1@email.com", "newemail2@email.com"]
    profile_services.update(
        combined_profile,
        first_name="Tom",
        last_name="Jones",
        primary_email="newpref@email.com",
        all_emails=emails,
    )

    combined_profile.refresh_from_db()
    assert combined_profile.first_name == "Tom"
    assert combined_profile.last_name == "Jones"
    assert combined_profile.primary_email == "newpref@email.com"
    assert combined_profile.emails == ["newemail1@email.com", "newemail2@email.com"]

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_change()
    assert log.user.pk == "via-api"
    assert log.object_repr == str(combined_profile)
    assert (
        log.get_change_message()
        == "Updating Profile record: first_name, last_name, primary_email, emails"
    )


def test_archive(combined_profile):
    assert combined_profile.is_active
    profile_services.archive(combined_profile)
    combined_profile.refresh_from_db()
    assert not combined_profile.is_active

    with pytest.raises(ProfileIsArchived) as ex:
        profile_services.archive(combined_profile)
        assert str(ex.value.args[0]) == "Profile is already archived"

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_change()
    assert log.user.pk == "via-api"
    assert log.object_repr == str(combined_profile)
    assert log.get_change_message() == "Archiving Profile record"


def test_unarchive(combined_profile):
    combined_profile.is_active = False
    combined_profile.save()
    combined_profile.refresh_from_db()
    assert not combined_profile.is_active
    profile_services.unarchive(combined_profile)
    combined_profile.refresh_from_db()
    assert combined_profile.is_active

    with pytest.raises(ProfileIsNotArchived) as ex:
        profile_services.unarchive(combined_profile)
        assert str(ex.value.args[0]) == "User is not archived"

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_change()
    assert log.user.pk == "via-api"
    assert log.object_repr == str(combined_profile)
    assert log.get_change_message() == "Unarchiving Profile record"


def test_delete_from_database(combined_profile):
    obj_repr = str(combined_profile)
    combined_profile.refresh_from_db()
    profile_services.delete_from_database(combined_profile)
    with pytest.raises(combined_profile.DoesNotExist):
        profile_services.get_by_id(combined_profile.sso_email_id, include_inactive=True)

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_deletion()
    assert log.user.pk == "via-api"
    assert log.object_repr == obj_repr
    assert log.get_change_message() == "Deleting Profile record"
