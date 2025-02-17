import pytest

from profiles.models import PeopleFinderProfile
from profiles.models.generic import Country
from profiles.services import peoplefinder as peoplefinder_services
from profiles.types import UNSET


pytestmark = pytest.mark.django_db


def test_get_by_id(peoplefinder_profile):
    # Get an active profile
    actual = peoplefinder_services.get_by_id(peoplefinder_profile.user.pk)
    assert actual.user.sso_email_id == peoplefinder_profile.user.sso_email_id

    # Get a soft-deleted profile when inactive profiles are included
    peoplefinder_profile.user.is_active = False
    peoplefinder_profile.user.save()

    soft_deleted_profile = peoplefinder_services.get_by_id(
        peoplefinder_profile.user.pk, include_inactive=True
    )
    assert soft_deleted_profile.user.is_active == False

    # Try to get a soft-deleted profile when inactive profiles are not included
    with pytest.raises(PeopleFinderProfile.DoesNotExist) as ex:
        # no custom error to keep overheads low
        peoplefinder_services.get_by_id(soft_deleted_profile.user.pk)

    assert ex.value.args[0] == "PeopleFinderProfile matching query does not exist."

    # Try to get a non-existent profile
    with pytest.raises(PeopleFinderProfile.DoesNotExist) as ex:
        peoplefinder_services.get_by_id("9999")
    assert str(ex.value.args[0]) == "PeopleFinderProfile matching query does not exist."


def test_update(peoplefinder_profile):
    # Create the default country
    Country.objects.create(reference_id="CTHMTC00260")

    # Check the first_name last_name and grade before update
    assert peoplefinder_profile.first_name == "John"
    assert peoplefinder_profile.last_name == "Doe"
    assert peoplefinder_profile.grade == "G7"

    peoplefinder_services.update(
        peoplefinder_profile=peoplefinder_profile,
        first_name="James",
        grade=UNSET,
    )
    # Check the first_name, last_name and grade after update
    assert peoplefinder_profile.first_name == "James"
    assert peoplefinder_profile.last_name == "Doe"
    assert peoplefinder_profile.grade == None
