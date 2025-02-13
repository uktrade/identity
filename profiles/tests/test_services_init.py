import datetime as dt

import pytest

from profiles import services
from profiles.models.generic import Country


pytestmark = pytest.mark.django_db


def test_get_by_id(mocker):
    mock_combined_get = mocker.patch(
        "profiles.services.combined.get_by_id", return_value="__combined__"
    )
    result = services.get_by_id("sso_id")
    mock_combined_get.assert_called_once_with(
        sso_email_id="sso_id", include_inactive=False
    )
    assert result == "__combined__"


def test_generate_combined_profile_data_accesses_profile_records(mocker):
    mock_sso_get = mocker.patch("profiles.services.staff_sso.get_by_id")
    mock_combined_get = mocker.patch("profiles.services.combined.get_by_id")
    services.generate_combined_profile_data(sso_email_id="sso_id")
    mock_sso_get.assert_called_once_with(sso_email_id="sso_id", include_inactive=True)
    mock_combined_get.assert_not_called()


def test_generate_combined_profile_data(sso_profile):
    email1 = sso_profile.emails.all()[0]
    email1.is_contact = True
    email1.save()
    assert not email1.is_primary
    assert email1.is_contact
    email2 = sso_profile.emails.all()[1]
    assert email2.is_primary
    assert not email2.is_contact

    data = services.generate_combined_profile_data(sso_profile.sso_email_id)
    assert data["first_name"] == sso_profile.first_name
    assert data["last_name"] == sso_profile.last_name
    assert data["primary_email"] == sso_profile.primary_email
    assert data["contact_email"] == sso_profile.contact_email
    assert data["emails"] == [email1.email.address, email2.email.address]
    assert data["is_active"] == sso_profile.user.is_active

    # no primary defaults to first email
    email2.is_primary = False
    email2.save()
    data = services.generate_combined_profile_data(sso_profile.sso_email_id)
    assert not email1.is_primary
    assert not email2.is_primary
    assert data["primary_email"] == sso_profile.emails.first().email.address

    # no contact defaults to primary
    email1.is_contact = False
    email1.save()
    data = services.generate_combined_profile_data(sso_profile.sso_email_id)
    assert not email1.is_contact
    assert not email2.is_contact
    assert data["contact_email"] == data["primary_email"]


def test_create_from_sso(mocker):
    mock_sso_create = mocker.patch("profiles.services.staff_sso.create")
    mock_combined_create = mocker.patch(
        "profiles.services.combined.create", return_value="__combined__"
    )
    mock_data = {
        "first_name": "Iggy",
        "last_name": "Vekath",
        "primary_email": "julia@synth.tic",
        "contact_email": "kev@dco.gov.uk",
        "emails": ["a@b.io"],
        "is_active": True,
    }
    mock_generate = mocker.patch(
        "profiles.services.generate_combined_profile_data",
        return_value=mock_data,
    )
    result = services.create_from_sso(
        sso_email_id="sso_id",
        first_name="Darius",
        last_name="Donnelly",
        all_emails=[
            "abe@zenithal.io",
            "gunter@yotam.gov.uk",
        ],
        primary_email="hardeep@xanthan.gum",
        contact_email="ethel@windlass.uk",
    )
    mock_sso_create.assert_called_once_with(
        sso_email_id="sso_id",
        first_name="Darius",
        last_name="Donnelly",
        all_emails=[
            "abe@zenithal.io",
            "gunter@yotam.gov.uk",
        ],
        primary_email="hardeep@xanthan.gum",
        contact_email="ethel@windlass.uk",
    )
    mock_generate.assert_called_once_with(sso_email_id="sso_id")
    mock_combined_create.assert_called_once_with(
        sso_email_id="sso_id",
        first_name=mock_data["first_name"],
        last_name=mock_data["last_name"],
        all_emails=mock_data["emails"],
        is_active=True,
        primary_email=mock_data["primary_email"],
        contact_email=mock_data["contact_email"],
    )
    assert result == "__combined__"


def test_update_from_peoplefinder(mocker, combined_profile, peoplefinder_profile):
    mock_pf_update = mocker.patch("profiles.services.peoplefinder.update")
    Country.objects.create(reference_id="CTHMTC00260")

    services.update_from_peoplefinder(
        profile=combined_profile,
        first_name="Jackson",
    )

    mock_pf_update.assert_called_once_with(
        peoplefinder_profile=peoplefinder_profile,
        first_name="Jackson",
        last_name=None,
        preferred_first_name=None,
        pronouns=None,
        name_pronunciation=None,
        email=None,
        contact_email=None,
        primary_phone_number=None,
        secondary_phone_number=None,
        photo=None,
        photo_small=None,
        grade=None,
        manager=None,
        not_employee=None,
        workdays=None,
        remote_working=None,
        usual_office_days=None,
        uk_office_location=None,
        location_in_building=None,
        international_building=None,
        country=None,
        professions=None,
        additional_roles=None,
        other_additional_roles=None,
        key_skills=None,
        other_key_skills=None,
        learning_interests=None,
        other_learning_interests=None,
        fluent_languages=None,
        intermediate_languages=None,
        previous_experience=None,
    )
    # TODO: Update test - Check for combined_profile updates after adding the functionality.
