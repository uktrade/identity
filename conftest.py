import datetime as dt

import pytest
from django.contrib.auth import get_user_model

from profiles.models.combined import Profile
from profiles.models.generic import Country, Email, UkStaffLocation
from profiles.models.peoplefinder import PeopleFinderProfile, PeopleFinderTeam
from profiles.models.staff_sso import StaffSSOProfile, StaffSSOProfileEmail


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
        grade="FCO S1",
        workdays=["Monday", "Tuesday"],
        professions=["Government commercial and contract management"],
        additional_roles=["Fire warden"],
        key_skills=["Asset management"],
        learning_interests=["Coding"],
        edited_or_confirmed_at=dt.datetime.now(),
    )


@pytest.fixture(scope="function")
def peoplefinder_team():
    return PeopleFinderTeam.objects.create(
        slug="9c8d532c-3d44-40fd-a512-debd26af007f",
        name="Team1Name",
        abbreviation="T1N",
        description="Team description",
        leaders_ordering="alphabetical",
        cost_code="CC1",
        team_type="standard",
    )


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
    return PeopleFinderProfile.objects.create(
        slug="734e7872-27f7-481b-9659-6632adf02268",
        user=manager_user,
        first_name="Jane",
        last_name="Manager",
        grade="G6",
        workdays=["Monday", "Tuesday"],
        professions=["Manager"],
        additional_roles=["Line Manager"],
        key_skills=["managing"],
        learning_interests=["management"],
        edited_or_confirmed_at=dt.datetime.now(),
    )
