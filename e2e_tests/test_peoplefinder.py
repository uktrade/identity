import json

import pytest
from django.test.client import Client
from django.urls import reverse

from profiles.models import Workday


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.e2e,
]


def test_get_workday(mocker):
    url = reverse("people-finder:get_workday")
    client = Client()
    response = client.get(
        url,
        content_type="application/json",
    )
    assert response.status_code == 200
    assert json.loads(response.content) == [
        {"key": key, "value": value} for key, value in Workday.choices
    ]

    mocker.patch(
        "core.services.get_workday",
        return_value={
            "Monday": "Mon",
            "Tuesday": "Tue",
            "Wednesday": "Wed",
            "Thursday": "Thu",
            "Friday": "Fri",
            "Saturday": "Sat",
            "Sunday": "Sun",
        },
    )
    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {
        "message": "Could not get workday options, reason: too many values to unpack (expected 2)"
    }

    mocker.patch(
        "core.services.get_workday", side_effect=Exception("mocked-test-exception")
    )

    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {
        "message": "Could not get workday options, reason: mocked-test-exception"
    }
