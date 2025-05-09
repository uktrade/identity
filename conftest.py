import datetime as dt

import pytest
from django.contrib.auth import get_user_model

from profiles.models.combined import Profile
from profiles.models.generic import Country, Email, UkStaffLocation
from profiles.models.peoplefinder import (
    PeopleFinderProfile,
    PeopleFinderTeam,
    PeopleFinderTeamTree,
)
from profiles.models.staff_sso import StaffSSOProfile, StaffSSOProfileEmail
from profiles.services.peoplefinder.team import get_root_team


pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture(autouse=True, scope="function")
def basic_user():
    return User.objects.create_user(
        sso_email_id="sso_email_id@email.com",
        is_active=True,
        is_staff=False,
        is_superuser=False,
    )


@pytest.fixture(scope="function")
def sso_profile(basic_user):
    email1 = Email.objects.create(address="email1@email.com")
    email2 = Email.objects.create(address="email2@email.com")
    sso_profile = StaffSSOProfile.objects.create(
        user=basic_user,
        first_name="John",
        last_name="Doe",
    )
    StaffSSOProfileEmail.objects.create(
        profile=sso_profile,
        email=email1,
        is_primary=False,
    )
    StaffSSOProfileEmail.objects.create(
        profile=sso_profile,
        email=email2,
        is_primary=True,
    )
    return sso_profile


@pytest.fixture(scope="function")
def combined_profile(sso_profile):
    return Profile.objects.create(
        sso_email_id=sso_profile.user.pk,
        first_name="John",
        last_name="Doe",
        primary_email="email2@email.com",
        contact_email="email@email.com",
        emails=[
            "email1@email.com",
            "email2@email.com",
        ],
        is_active=True,
    )


@pytest.fixture(scope="function")
def peoplefinder_profile(basic_user):
    email = Email.objects.create(address="john.doe@example.com")
    contact_email = Email.objects.create(address="john.doe_contact@example.com")
    return PeopleFinderProfile.objects.create(
        slug="9c8d532c-3d44-40fd-a512-debd26af007f",
        user=basic_user,
        first_name="John",
        last_name="Doe",
        email=email,
        contact_email=contact_email,
        grade="grade_7",
        workdays=["mon", "tue"],
        professions=["commercial"],
        additional_roles=["fire_warden"],
        key_skills=["asset_management"],
        learning_interests=["coding"],
        edited_or_confirmed_at=dt.datetime.now(),
    )


@pytest.fixture(scope="function")
def peoplefinder_team():
    return get_root_team()


@pytest.fixture(autouse=True, scope="function")
def default_country():
    return Country.objects.create(
        reference_id="CTHMTC00260",
        name="UK",
        type="country",
        iso_1_code="31",
        iso_2_code="66",
        iso_3_code="2",
    )


@pytest.fixture(autouse=True, scope="function")
def uk_staff_location():
    return UkStaffLocation.objects.create(
        code="location_1",
        name="OAB_UK",
        city="London",
        organisation="DBT",
        building_name="OAB",
    )


@pytest.fixture(scope="function")
def manager_user():
    return User.objects.create_user(
        sso_email_id="manager_sso_email@email.com",
        is_active=True,
        is_staff=False,
        is_superuser=False,
    )


@pytest.fixture(scope="function")
def manager(manager_user):
    email = Email.objects.create(address="jane@email.com")
    contact_email = Email.objects.create(address="jane_contact@email.com")
    return PeopleFinderProfile.objects.create(
        slug="734e7872-27f7-481b-9659-6632adf02268",
        user=manager_user,
        first_name="Jane",
        last_name="Manager",
        email=email,
        contact_email=contact_email,
        grade="grade_6",
        workdays=["mon", "wed"],
        professions=["gov_it"],
        additional_roles=["cirrus_champion"],
        key_skills=["coaching"],
        learning_interests=["mentoring"],
        edited_or_confirmed_at=dt.datetime.now(),
    )
