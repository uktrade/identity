import pytest
from django.contrib.admin.models import LogEntry

from profiles.models.generic import Email
from profiles.models.staff_sso import StaffSSOProfile, StaffSSOProfileEmail
from profiles.services import staff_sso as staff_sso_services


pytestmark = pytest.mark.django_db


def test_create(basic_user):
    assert LogEntry.objects.count() == 0
    assert Email.objects.count() == 0
    assert StaffSSOProfile.objects.count() == 0
    assert StaffSSOProfileEmail.objects.count() == 0
    staff_sso_services.create(
        sso_email_id=basic_user.pk,
        first_name="John",
        last_name="Doe",
        all_emails=[
            "email1@email.com",
            "email2@email.com",
        ],
        primary_email="email2@email.com",
    )

    # assert 2 email records created
    assert Email.objects.count() == 2
    assert Email.objects.first().address == "email1@email.com"
    assert Email.objects.last().address == "email2@email.com"

    # assert staff sso profile created
    assert StaffSSOProfile.objects.count() == 1
    assert StaffSSOProfile.objects.first().first_name == "John"
    assert StaffSSOProfile.objects.first().last_name == "Doe"
    assert StaffSSOProfile.objects.first().user.sso_email_id == basic_user.pk

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_addition()
    assert log.user.pk == "via-api"
    assert log.object_repr == str(StaffSSOProfile.objects.first())
    assert log.get_change_message() == "Creating new StaffSSOProfile"

    # assert staff sso email created
    assert StaffSSOProfileEmail.objects.count() == 2
    assert StaffSSOProfileEmail.objects.first().email.address == "email1@email.com"
    assert not StaffSSOProfileEmail.objects.first().is_primary
    assert StaffSSOProfileEmail.objects.last().email.address == "email2@email.com"
    assert StaffSSOProfileEmail.objects.last().is_primary
    assert StaffSSOProfileEmail.objects.first().profile.first_name == "John"
    assert StaffSSOProfileEmail.objects.first().profile.last_name == "Doe"
    assert StaffSSOProfileEmail.objects.last().profile.first_name == "John"
    assert StaffSSOProfileEmail.objects.last().profile.last_name == "Doe"


def test_get_by_user_id(sso_profile):
    actual = staff_sso_services.get_by_id(sso_profile.user.pk)
    assert actual.user.sso_email_id == sso_profile.user.pk
    assert actual.first_name == sso_profile.first_name
    assert actual.last_name == sso_profile.last_name


def test_update(sso_profile):
    emails = [
        "email2@email.com",
    ]

    # check values before update
    staff_sso_email = StaffSSOProfileEmail.objects.filter(
        email=Email.objects.get(address="email2@email.com")
    )[0]
    assert staff_sso_email.is_primary
    assert sso_profile.first_name == sso_profile.first_name
    assert sso_profile.last_name == sso_profile.last_name

    staff_sso_services.update(
        sso_email_id=sso_profile.user.pk,
        first_name="newTom",
        last_name="newJones",
        all_emails=emails,
    )
    sso_profile.refresh_from_db()

    assert sso_profile.first_name == "newTom"
    assert sso_profile.last_name == "newJones"
    staff_sso_email = StaffSSOProfileEmail.objects.filter(
        email=Email.objects.get(address="email2@email.com")
    )[0]
    assert not staff_sso_email.is_primary

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_change()
    assert log.user.pk == "via-api"
    assert log.object_repr == str(sso_profile)
    assert (
        log.get_change_message()
        == "Updating StaffSSOProfile record: first_name, last_name"
    )
