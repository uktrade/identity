import json

import pytest
from django.test.client import Client
from django.urls import reverse

from profiles.models.generic import Country, UkStaffLocation


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.e2e,
]


def test_get_countries(mocker):
    url = reverse("people-finder:get_countries")
    client = Client()
    response = client.get(
        url,
        content_type="application/json",
    )

    expected = list(
        Country.objects.values(
            "reference_id",
            "name",
            "type",
            "iso_1_code",
            "iso_2_code",
            "iso_3_code",
            "overseas_region",
            "start_date",
            "end_date",
        )
    )

    assert response.status_code == 200
    assert json.loads(response.content) == expected

    mocker.patch(
        "core.services.get_countries",
        side_effect=Exception("mocked-test-exception"),
    )

    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {
        "message": "Could not get Countries, reason: mocked-test-exception"
    }


def test_get_uk_staff_locations(mocker):
    url = reverse("people-finder:get_uk_staff_locations")
    client = Client()
    response = client.get(
        url,
        content_type="application/json",
    )

    expected = list(
        UkStaffLocation.objects.values(
            "code",
            "name",
            "organisation",
            "building_name",
        )
    )

    assert response.status_code == 200
    assert json.loads(response.content) == expected

    mocker.patch(
        "core.services.get_uk_staff_locations",
        side_effect=Exception("mocked-test-exception"),
    )

    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {
        "message": "Could not get UK staff locations, reason: mocked-test-exception"
    }
