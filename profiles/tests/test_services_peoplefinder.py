import pytest
from django.contrib.admin.models import LogEntry

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


def test_delete_from_database(peoplefinder_profile):
    obj_repr = str(peoplefinder_profile)
    peoplefinder_profile.refresh_from_db()
    peoplefinder_services.delete_from_database(peoplefinder_profile)
    with pytest.raises(peoplefinder_profile.DoesNotExist):
        peoplefinder_services.get_by_id(
            sso_email_id=peoplefinder_profile.user.sso_email_id, include_inactive=True
        )

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_deletion()
    assert log.user.pk == "via-api"
    assert log.object_repr == obj_repr
    assert log.get_change_message() == "Deleting People Finder Profile record"
