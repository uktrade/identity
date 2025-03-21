import datetime as dt

import pytest

from profiles import services
from profiles.exceptions import NonCombinedProfileExists
from profiles.models import PeopleFinderProfile
from profiles.models.combined import Profile
from profiles.models.staff_sso import StaffSSOProfile
from profiles.services.peoplefinder import profile as peoplefinder_services


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
    mock_pf_update = mocker.patch("profiles.services.peoplefinder.profile.update")
    services.update_from_peoplefinder(
        profile=combined_profile,
        is_active=combined_profile.is_active,
        slug=peoplefinder_profile.slug,
        first_name="Jackson",
    )

    mock_pf_update.assert_called_once_with(
        peoplefinder_profile=peoplefinder_profile,
        is_active=True,
        became_inactive=None,
        edited_or_confirmed_at=None,
        login_count=None,
        first_name="Jackson",
        last_name=None,
        preferred_first_name=None,
        pronouns=None,
        name_pronunciation=None,
        email_address=None,
        contact_email_address=None,
        primary_phone_number=None,
        secondary_phone_number=None,
        photo=None,
        photo_small=None,
        grade=None,
        manager_slug=None,
        not_employee=None,
        workdays=None,
        remote_working=None,
        usual_office_days=None,
        uk_office_location_id=None,
        location_in_building=None,
        international_building=None,
        country_id=None,
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


def test_update_peoplefinder_team(mocker, peoplefinder_team):
    mock_pft_update_team = mocker.patch(
        "profiles.services.peoplefinder.team.update_team"
    )
    services.update_peoplefinder_team(
        slug=peoplefinder_team.slug,
        name=peoplefinder_team.name,
        abbreviation=peoplefinder_team.abbreviation,
        description="New description",
        leaders_ordering=peoplefinder_team.leaders_ordering,
        cost_code=peoplefinder_team.cost_code,
        team_type=peoplefinder_team.team_type,
    )

    mock_pft_update_team.assert_called_once_with(
        peoplefinder_team=peoplefinder_team,
        name=peoplefinder_team.name,
        abbreviation=peoplefinder_team.abbreviation,
        description="New description",
        leaders_ordering=peoplefinder_team.leaders_ordering,
        cost_code=peoplefinder_team.cost_code,
        team_type=peoplefinder_team.team_type,
    )


def test_delete_combined_profile(combined_profile, sso_profile) -> None:
    all_profiles = services.get_all_profiles(sso_email_id=combined_profile.sso_email_id)

    # Fail to delete a combined profile as the user has other profiles
    with pytest.raises(NonCombinedProfileExists) as ex:
        services.delete_combined_profile(all_profiles)
    assert str(ex.value.args[0]) == f"All existing profiles: {all_profiles.keys()}"

    # Delete the SSO profile, then successfully delete the combined profile.
    services.delete_sso_profile(sso_profile)
    del all_profiles["sso"]

    services.delete_combined_profile(all_profiles)

    with pytest.raises(Profile.DoesNotExist) as ex:
        services.get_by_id(combined_profile.sso_email_id)
    assert str(ex.value.args[0]) == "Profile matching query does not exist."


def test_delete_sso_profile(sso_profile) -> None:
    # Successfully delete a SSO profile
    services.delete_sso_profile(sso_profile)
    with pytest.raises(StaffSSOProfile.DoesNotExist) as ex:
        services.staff_sso.get_by_id(sso_profile.user.sso_email_id)
    assert str(ex.value.args[0]) == "StaffSSOProfile matching query does not exist."


def test_delete_peoplefinder_profile(peoplefinder_profile) -> None:
    # Successfully delete a People Finder profile
    services.delete_peoplefinder_profile(peoplefinder_profile)
    with pytest.raises(PeopleFinderProfile.DoesNotExist) as ex:
        peoplefinder_services.get_by_slug(
            slug=peoplefinder_profile.slug,
            include_inactive=True,
        )
    assert str(ex.value.args[0]) == "PeopleFinderProfile matching query does not exist."


def test_create_peoplefinder_team(mocker):
    mock_pf_create_team = mocker.patch(
        "profiles.services.peoplefinder.team.create_team"
    )
    services.create_peoplefinder_team(
        slug="employee-experience",
        name="Employee Experience",
        abbreviation="EX",
        description="We support the platforms, products, tools and services that help our colleagues to do their jobs.",
        leaders_ordering="custom",
        cost_code="EX_cost_code",
        team_type="portfolio",
    )

    mock_pf_create_team.assert_called_once_with(
        slug="employee-experience",
        name="Employee Experience",
        abbreviation="EX",
        description="We support the platforms, products, tools and services that help our colleagues to do their jobs.",
        leaders_ordering="custom",
        cost_code="EX_cost_code",
        team_type="portfolio",
    )
