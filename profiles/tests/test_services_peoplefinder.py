import pytest

from profiles.models.generic import Country
from profiles.services import peoplefinder as peoplefinder_services
from profiles.types import UNSET


pytestmark = pytest.mark.django_db


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
