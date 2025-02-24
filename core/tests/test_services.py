import datetime as dt
from unittest.mock import call

import pytest

from conftest import basic_user
from core import services
from core.services import (
    SSO_CONTACT_EMAIL_ADDRESS,
    SSO_EMAIL_ADDRESSES,
    SSO_FIRST_NAME,
    SSO_LAST_NAME,
    SSO_USER_EMAIL_ID,
    SSO_USER_STATUS,
)
from profiles import services as profile_services
from profiles.models import PeopleFinderProfile
from profiles.models.combined import Profile
from profiles.models.generic import Country, Email
from profiles.models.staff_sso import StaffSSOProfile
from profiles.services import peoplefinder as peoplefinder_services
from profiles.services import staff_sso as sso_profile_services
from user import services as user_services
from user.exceptions import UserExists
from user.models import User


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("basic_user", [None])
def test_create_identity(mocker):
    mock_user_create = mocker.patch("user.services.create")
    mock_profiles_create = mocker.patch(
        "profiles.services.create_from_sso",
        return_value="__profile__",
    )
    # User is created
    profile = services.create_identity(
        id="billy.sso.email.id@gov.uk",
        first_name="Billy",
        last_name="Bob",
        all_emails=[
            "test@test.com",
            "test2@test.com",
            "test3@test.com",
        ],
        is_active=False,
        primary_email="test2@test.com",
        contact_email="test3@test.com",
    )
    mock_user_create.assert_called_once_with(
        sso_email_id="billy.sso.email.id@gov.uk",
        is_active=False,
    )
    mock_profiles_create.assert_called_once_with(
        sso_email_id="billy.sso.email.id@gov.uk",
        first_name="Billy",
        last_name="Bob",
        all_emails=[
            "test@test.com",
            "test2@test.com",
            "test3@test.com",
        ],
        primary_email="test2@test.com",
        contact_email="test3@test.com",
    )
    assert profile == "__profile__"


def test_existing_user(basic_user) -> None:
    with pytest.raises(UserExists):
        services.create_identity(
            id=basic_user.pk,
            first_name="Billy",
            last_name="Bob",
            all_emails=["new_user@email.gov.uk"],
            is_active=True,
        )


def test_new_user() -> None:
    profile = services.create_identity(
        id="new_user@gov.uk",
        first_name="Billy",
        last_name="Bob",
        all_emails=["new_user@email.gov.uk"],
        is_active=True,
    )
    assert isinstance(profile, Profile)
    assert profile.pk
    assert profile.sso_email_id == "new_user@gov.uk"
    assert user_services.get_by_id(
        sso_email_id="new_user@gov.uk", include_inactive=True
    )


def test_update_identity() -> None:
    profile = services.create_identity(
        "new_user@gov.uk",
        "Billy",
        "Bob",
        ["new_user@email.gov.uk"],
        is_active=True,
    )
    assert user_services.get_by_id(
        sso_email_id="new_user@gov.uk", include_inactive=True
    ).is_active

    services.update_identity(
        profile,
        first_name="Joe",
        last_name="Bobby",
        all_emails=["new_user@email.gov.uk"],
        is_active=False,
    )
    profile.refresh_from_db()

    assert profile.first_name == "Joe"
    assert profile.last_name == "Bobby"
    assert not user_services.get_by_id(
        sso_email_id="new_user@gov.uk",
        include_inactive=True,
    ).is_active


def test_delete_identity() -> None:
    profile = services.create_identity(
        id="new_user@gov.uk",
        first_name="Billy",
        last_name="Bob",
        all_emails=["new_user@email.gov.uk"],
        is_active=True,
    )

    user = User.objects.get(sso_email_id=profile.sso_email_id)
    PeopleFinderProfile.objects.create(
        user=user,
        workdays=["Monday, Tuesday"],
        professions=["COMMERCIAL"],
        additional_roles=["FIRE_WARDEN"],
        key_skills=["ASSET_MANAGEMENT"],
        learning_interests=["SHADOWING"],
        edited_or_confirmed_at=dt.datetime.now(),
    )

    services.delete_identity(
        profile,
    )
    with pytest.raises(Profile.DoesNotExist) as pex:
        services.get_identity_by_id(
            id=profile.sso_email_id,
            include_inactive=True,
        )

    assert str(pex.value.args[0]) == "Profile matching query does not exist."

    # check that people finder profile has been deleted
    with pytest.raises(PeopleFinderProfile.DoesNotExist) as pfex:
        PeopleFinderProfile.objects.get(
            user__sso_email_id=user.sso_email_id,
        )
    assert (
        str(pfex.value.args[0]) == "PeopleFinderProfile matching query does not exist."
    )

    # check that sso profile has been deleted
    with pytest.raises(StaffSSOProfile.DoesNotExist) as pfex:
        sso_profile_services.get_by_id(
            sso_email_id=user.sso_email_id,
            include_inactive=True,
        )
    assert str(pfex.value.args[0]) == "StaffSSOProfile matching query does not exist."

    with pytest.raises(User.DoesNotExist) as uex:
        user_services.get_by_id(
            sso_email_id="new_user@gov.uk",
            include_inactive=True,
        )

    assert str(uex.value.args[0]) == "User does not exist"


def test_update_peoplefinder_profile(combined_profile, peoplefinder_profile, manager):
    # Create a new country to update the existing one
    Country.objects.create(
        reference_id="country2",
        name="country2",
        type="country",
        iso_1_code="33",
        iso_2_code="63",
        iso_3_code="23",
    )

    services.update_peoplefinder_profile(
        profile=combined_profile,
        slug=peoplefinder_profile.slug,
        is_active=combined_profile.is_active,
        email_address="new_super_fancy_email@gov.uk",
        country_id="country2",
        uk_office_location_id="location_1",
        manager_slug=manager.slug,
    )

    peoplefinder_profile.refresh_from_db()
    assert peoplefinder_profile.email.address == "new_super_fancy_email@gov.uk"
    assert peoplefinder_profile.country.reference_id == "country2"
    assert peoplefinder_profile.uk_office_location.code == "location_1"
    assert peoplefinder_profile.manager == manager

    # Delete identity and try to update the peoplefinder profile
    services.delete_identity(profile=combined_profile)

    with pytest.raises(PeopleFinderProfile.DoesNotExist):
        services.update_peoplefinder_profile(
            profile=combined_profile,
            slug=peoplefinder_profile.slug,
            is_active=combined_profile.is_active,
            email_address="new_super_fancy_email@gov.uk",
            country_id="country2",
            uk_office_location_id="location_1",
            manager_slug=manager.slug,
        )
