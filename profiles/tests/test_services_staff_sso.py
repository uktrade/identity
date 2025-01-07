import pytest
from django.contrib.admin.models import LogEntry

from profiles.models.generic import Email
from profiles.models.staff_sso import StaffSSOProfile, StaffSSOProfileEmail
from profiles.services import staff_sso as staff_sso_services


pytestmark = pytest.mark.django_db


def test_get_by_id(sso_profile):
    actual = staff_sso_services.get_by_id(sso_profile.user.pk)
    assert actual.user.sso_email_id == sso_profile.user.sso_email_id

    # Try to get a soft-deleted profile
    sso_profile.user.is_active = False
    sso_profile.user.save()
    with pytest.raises(StaffSSOProfile.DoesNotExist) as ex:
        # no custom error to keep overheads low
        staff_sso_services.get_by_id(sso_profile.user.pk)
        assert ex.value.args[0] == "User has been previously deleted"

    # or a non-existent one
    with pytest.raises(StaffSSOProfile.DoesNotExist) as ex:
        staff_sso_services.get_by_id("9999")
        assert str(ex.value.args[0]) == "User does not exist"


def test_create(basic_user):
    assert StaffSSOProfile.objects.count() == 0
    assert Email.objects.count() == 0
    assert StaffSSOProfileEmail.objects.count() == 0

    with pytest.raises(ValueError) as ex:
        staff_sso_services.create(
            sso_email_id=basic_user.pk,
            first_name="John",
            last_name="Doe",
            all_emails=[
                "email1@email.com",
                "email2@email.com",
                "email3@email.com",
            ],
            primary_email="email@email.com",
            contact_email="email1@email.com",
        )
        assert str(ex.value.args[0]) == "primary_email not in all_emails"

    with pytest.raises(ValueError) as ex:
        staff_sso_services.create(
            sso_email_id=basic_user.pk,
            first_name="John",
            last_name="Doe",
            all_emails=[
                "email1@email.com",
                "email2@email.com",
                "email3@email.com",
            ],
            primary_email="email1@email.com",
            contact_email="email@email.com",
        )
        assert str(ex.value.args[0]) == "contact_email not in all_emails"

    profile = staff_sso_services.create(
        sso_email_id=basic_user.pk,
        first_name="John",
        last_name="Doe",
        all_emails=[
            "email1@email.com",
            "email2@email.com",
            "email3@email.com",
        ],
        primary_email="email2@email.com",
        contact_email="email1@email.com",
    )

    # assert all email records created
    assert Email.objects.count() == 3
    assert Email.objects.filter(address="email1@email.com")
    assert Email.objects.filter(address="email2@email.com")
    assert Email.objects.filter(address="email3@email.com")

    # assert staff sso profile created
    assert StaffSSOProfile.objects.count() == 1
    assert profile == StaffSSOProfile.objects.first()
    assert profile.primary_email == "email2@email.com"
    assert profile.contact_email == "email1@email.com"

    # assert staff sso email created
    assert StaffSSOProfileEmail.objects.count() == 3
    pe1 = StaffSSOProfileEmail.objects.get(
        profile=profile,
        email=Email.objects.get(address="email1@email.com"),
    )
    pe2 = StaffSSOProfileEmail.objects.get(
        profile=profile,
        email=Email.objects.get(address="email2@email.com"),
    )
    pe3 = StaffSSOProfileEmail.objects.get(
        profile=profile,
        email=Email.objects.get(address="email3@email.com"),
    )
    assert not pe1.is_primary
    assert pe2.is_primary
    assert not pe3.is_primary
    assert pe1.is_contact
    assert not pe2.is_contact
    assert not pe3.is_contact

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_addition()
    assert log.user.pk == "via-api"
    assert log.object_repr == str(StaffSSOProfile.objects.first())
    assert log.get_change_message() == "Creating new StaffSSOProfile"


@pytest.mark.skip("waiting for updated functionality to under primary")
def test_update(sso_profile):
    emails = ["email2@email.com"]
    # check values before update
    staff_sso_email = StaffSSOProfileEmail.objects.get(
        email=Email.objects.get(address=emails[0])
    )

    with pytest.raises(ValueError) as ex:
        staff_sso_services.update(
            staff_sso_profile=sso_profile,
            first_name="John",
            last_name="Doe",
            all_emails=[
                "email1@email.com",
                "email2@email.com",
                "email3@email.com",
            ],
            primary_email="email@email.com",
            contact_email="email1@email.com",
        )
        assert str(ex.value.args[0]) == "primary_email not in all_emails"

    with pytest.raises(ValueError) as ex:
        staff_sso_services.update(
            staff_sso_profile=sso_profile,
            first_name="John",
            last_name="Doe",
            all_emails=[
                "email1@email.com",
                "email2@email.com",
                "email3@email.com",
            ],
            primary_email="email1@email.com",
            contact_email="email@email.com",
        )
        assert str(ex.value.args[0]) == "contact_email not in all_emails"

    assert staff_sso_email.is_primary
    assert sso_profile.emails.count() == 2
    staff_sso_services.update(
        staff_sso_profile=sso_profile,
        first_name="newTom",
        last_name="newJones",
        all_emails=emails,
    )
    sso_profile.refresh_from_db()
    staff_sso_email.refresh_from_db()
    assert sso_profile.first_name == "newTom"
    assert sso_profile.last_name == "newJones"
    assert not staff_sso_email.is_primary
    assert sso_profile.emails.count() == 1

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_change()
    assert log.user.pk == "via-api"
    assert log.object_repr == str(sso_profile)
    assert (
        log.get_change_message()
        == "Updating StaffSSOProfile record: first_name, last_name"
    )


def test_set_email_details(sso_profile):
    email = Email.objects.create(address="andy@adams.com")
    second_email = Email.objects.create(address="barney@bates.com")
    #
    # Through record
    #
    # no through record exists
    with pytest.raises(StaffSSOProfileEmail.DoesNotExist):
        assert StaffSSOProfileEmail.objects.get(
            profile=sso_profile,
            email=email,
        )
    staff_sso_services.set_email_details(
        profile=sso_profile,
        email=email,
    )
    # through record created
    assert StaffSSOProfileEmail.objects.get(
        profile=sso_profile,
        email=email,
    )
    # existing through record allowed
    staff_sso_services.set_email_details(
        profile=sso_profile,
        email=email,
    )
    #
    # Primary email
    #
    assert sso_profile.primary_email != email.address
    staff_sso_services.set_email_details(
        profile=sso_profile,
        email=email,
        is_primary=True,
    )
    assert sso_profile.primary_email == email.address
    # only 1 primary address allowed
    assert (
        StaffSSOProfileEmail.objects.filter(
            profile=sso_profile, is_primary=True
        ).count()
        == 1
    )
    staff_sso_services.set_email_details(
        profile=sso_profile,
        email=second_email,
        is_primary=True,
    )
    assert sso_profile.primary_email == second_email.address
    assert (
        StaffSSOProfileEmail.objects.filter(
            profile=sso_profile, is_primary=True
        ).count()
        == 1
    )
    #
    #  Contact email
    #
    assert (
        StaffSSOProfileEmail.objects.filter(
            profile=sso_profile, is_contact=True
        ).count()
        == 0
    )
    assert sso_profile.contact_email is None
    staff_sso_services.set_email_details(
        profile=sso_profile,
        email=email,
        is_contact=True,
    )
    assert sso_profile.contact_email == email.address  # type: ignore
    assert (
        StaffSSOProfileEmail.objects.filter(
            profile=sso_profile, is_contact=True
        ).count()
        == 1
    )
    staff_sso_services.set_email_details(
        profile=sso_profile,
        email=second_email,
        is_contact=True,
    )
    assert sso_profile.contact_email == second_email.address  # type: ignore
    assert (
        StaffSSOProfileEmail.objects.filter(
            profile=sso_profile, is_contact=True
        ).count()
        == 1
    )
