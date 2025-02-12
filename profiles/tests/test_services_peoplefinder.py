import pytest

from profiles.models.generic import Country
from profiles.services import peoplefinder as peoplefinder_services


pytestmark = pytest.mark.django_db


def test_update(peoplefinder_profile):
    # Create the default country
    UK = Country.objects.create(reference_id="CTHMTC00260")

    # Check the first_name and grade before update
    assert peoplefinder_profile.first_name == "John"
    assert peoplefinder_profile.grade == "G7"

    peoplefinder_services.update(
        peoplefinder_profile=peoplefinder_profile,
        first_name="James",
        preferred_first_name=None,
        last_name="Doe",
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
        not_employee=False,
        workdays=["Monday", "Tuesday"],
        remote_working=None,
        usual_office_days=None,
        uk_office_location=None,
        location_in_building=None,
        international_building=None,
        country=UK,
        professions=["Developer"],
        additional_roles=["BA"],
        other_additional_roles=None,
        key_skills=["coding"],
        other_key_skills=None,
        learning_interests=["everything"],
        other_learning_interests=None,
        fluent_languages=None,
        intermediate_languages=None,
        previous_experience=None,
    )
    # Check the first_name and grade after update
    assert peoplefinder_profile.first_name == "James"
    assert peoplefinder_profile.grade == None
