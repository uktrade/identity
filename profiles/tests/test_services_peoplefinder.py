import pytest
from django.contrib.admin.models import LogEntry

from profiles.models import PeopleFinderProfile
from profiles.services import peoplefinder as peoplefinder_services


pytestmark = pytest.mark.django_db


def test_delete_from_database(peoplefinder_profile):
    obj_repr = str(peoplefinder_profile)
    peoplefinder_profile.refresh_from_db()
    peoplefinder_services.delete_from_database(peoplefinder_profile)
    with pytest.raises(peoplefinder_profile.DoesNotExist):
        peoplefinder_services.get_by_id(peoplefinder_profile.user.sso_email_id)

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_deletion()
    assert log.user.pk == "via-api"
    assert log.object_repr == obj_repr
    assert log.get_change_message() == "Deleting People Finder Profile record"


def test_delete_from_database_no_pf_profile():
    with pytest.raises(PeopleFinderProfile.DoesNotExist) as ex:
        peoplefinder_services.delete_from_database(peoplefinder_profile=None)

    assert "Please provide peoplefinder_profile to be deleted" in str(ex.value)