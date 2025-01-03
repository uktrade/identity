import pytest

from django.contrib.admin.models import LogEntry

from profiles.models.combined import Profile
from profiles.services import combined as profile_services


pytestmark = pytest.mark.django_db


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
    )
    assert created_profile.sso_email_id == "email@email.com"
    assert created_profile.first_name == "John"
    assert created_profile.last_name == "Doe"
    assert created_profile.primary_email == "email2@email.com"
    assert created_profile.emails, ["email1@email.com" == "email2@email.com"]

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_addition()
    assert log.user.pk == "via-api"
    assert log.object_repr == str(created_profile)
    assert log.get_change_message() == "Creating new Profile"


def test_get_by_id(combined_profile):
    get_profile_result = profile_services.get_by_id(combined_profile.sso_email_id)

    assert get_profile_result.sso_email_id == combined_profile.sso_email_id
    assert get_profile_result.first_name == combined_profile.first_name
    assert get_profile_result.last_name == combined_profile.last_name
    assert get_profile_result.primary_email == combined_profile.primary_email
    assert get_profile_result.emails == combined_profile.emails


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
    profile_services.archive(combined_profile)

    combined_profile.refresh_from_db()
    assert not combined_profile.is_active

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
    profile_services.unarchive(combined_profile)
    combined_profile.refresh_from_db()
    assert combined_profile.is_active

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
        profile_services.get_by_id(combined_profile.sso_email_id)

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_deletion()
    assert log.user.pk == "via-api"
    assert log.object_repr == obj_repr
    assert log.get_change_message() == "Deleting Profile record"
