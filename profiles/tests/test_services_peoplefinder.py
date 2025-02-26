import uuid

import pytest
from django.contrib.admin.models import LogEntry

from profiles.models import PeopleFinderProfile
from profiles.models.generic import Country, Grade, UkStaffLocation
from profiles.services import peoplefinder as peoplefinder_services
from profiles.types import UNSET
from user.models import User


pytestmark = pytest.mark.django_db


def test_create(peoplefinder_profile):
    # Create staff location
    UkStaffLocation.objects.create(
        code="test",
        name="test_name",
        city="test_city",
        organisation="test_organisation",
        building_name="test_building_name",
    )

    # Manager
    manager = peoplefinder_profile

    # User
    user = User.objects.create(sso_email_id="tom@email.com")

    peoplefinder_profile = peoplefinder_services.create(
        slug=str(uuid.uuid4()),
        user=user,
        is_active=user.is_active,
        first_name="Tom",
        last_name="Doe",
        grade="GRADE_7",
        country_id="CTHMTC00260",
        uk_office_location_id="test",
        manager_slug=manager.slug,
    )

    assert peoplefinder_profile.first_name == "Tom"
    assert peoplefinder_profile.last_name == "Doe"
    assert peoplefinder_profile.grade == "GRADE_7"
    assert peoplefinder_profile.uk_office_location == UkStaffLocation.objects.get(
        code="test"
    )
    assert peoplefinder_profile.manager == manager


def test_update(peoplefinder_profile, combined_profile):
    # Check the first_name last_name and grade before update
    assert peoplefinder_profile.first_name == "John"
    assert peoplefinder_profile.last_name == "Doe"
    assert peoplefinder_profile.grade == "G7"

    peoplefinder_services.update(
        peoplefinder_profile=peoplefinder_profile,
        is_active=combined_profile.is_active,
        first_name="James",
        grade=UNSET,
    )
    # Check the first_name, last_name and grade after update
    assert peoplefinder_profile.first_name == "James"
    assert peoplefinder_profile.last_name == "Doe"
    assert peoplefinder_profile.is_active == combined_profile.is_active
    assert peoplefinder_profile.grade == None


def test_delete_from_database(peoplefinder_profile):
    obj_repr = str(peoplefinder_profile)
    peoplefinder_profile.refresh_from_db()
    peoplefinder_services.delete_from_database(peoplefinder_profile)
    with pytest.raises(peoplefinder_profile.DoesNotExist):
        peoplefinder_services.get_by_slug(
            slug=peoplefinder_profile.slug, include_inactive=True
        )

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_deletion()
    assert log.user.pk == "via-api"
    assert log.object_repr == obj_repr
    assert log.get_change_message() == "Deleting People Finder Profile record"


def test_get_by_id(peoplefinder_profile):
    # Get an active people finder profile
    actual = peoplefinder_services.get_by_slug(slug=peoplefinder_profile.slug)
    assert actual.user.sso_email_id == peoplefinder_profile.user.sso_email_id

    # Get a soft-deleted people finder profile when inactive profiles are included
    peoplefinder_profile.is_active = False
    peoplefinder_profile.save()

    soft_deleted_profile = peoplefinder_services.get_by_slug(
        peoplefinder_profile.slug, include_inactive=True
    )
    assert soft_deleted_profile.is_active == False

    # Try to get a soft-deleted profile when inactive profiles are not included
    with pytest.raises(PeopleFinderProfile.DoesNotExist) as ex:
        # no custom error to keep overheads low
        peoplefinder_services.get_by_slug(slug=soft_deleted_profile.slug)

    assert ex.value.args[0] == "PeopleFinderProfile matching query does not exist."

    # Try to get a non-existent profile
    with pytest.raises(PeopleFinderProfile.DoesNotExist) as ex:
        peoplefinder_services.get_by_slug(slug="550e8400-e29b-41d4-a716-446655440000")
    assert str(ex.value.args[0]) == "PeopleFinderProfile matching query does not exist."


def test_get_countries():
    countries = peoplefinder_services.get_countries()
    # Check if country properties exist in fetched country
    expected = {
        "reference_id": "CTHMTC00260",
        "name": "UK",
        "type": "country",
        "iso_1_code": "31",
        "iso_2_code": "66",
        "iso_3_code": "2",
        "overseas_region": None,
        "start_date": None,
        "end_date": None,
    }
    assert expected.items() <= countries[0].__dict__.items()


def test_get_uk_staff_locations():
    locations = peoplefinder_services.get_uk_staff_locations()
    # Check if code, name, organisation and building_name exists in the location dict
    assert {
        "code": "location_1",
        "name": "OAB_UK",
        "organisation": "DBT",
        "building_name": "OAB",
    }.items() <= locations[0].__dict__.items()


def test_get_workday_options():
    options = peoplefinder_services.get_workday()

    assert options == [
        ("Monday", "Mon"),
        ("Tuesday", "Tue"),
        ("Wednesday", "Wed"),
        ("Thursday", "Thu"),
        ("Friday", "Fri"),
        ("Saturday", "Sat"),
        ("Sunday", "Sun"),
    ]
