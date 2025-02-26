import json

import pytest
from django.test.client import Client
from django.urls import reverse

from profiles.models.peoplefinder import RemoteWorking


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.e2e,
]


def test_get_remote_working(mocker):
    url = reverse("people-finder:get_remote_working")
    client = Client()
    response = client.get(
        url,
        content_type="application/json",
    )
    assert response.status_code == 200
    assert json.loads(response.content) == [
        {"key": key, "value": value} for key, value in RemoteWorking.choices
    ]

    mocker.patch(
        "core.services.get_remote_working",
        return_value={
            "remote_worker": "REMOTE WORKER",
            "office_worker": "OFFICE WORKER",
        },
    )
    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {'message': 'Could not get remote working options, reason: too many values to unpack (expected 2)'}

    mocker.patch(
        "core.services.get_remote_working",
        side_effect=Exception("mocked-test-exception")
    )

    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {'message': 'Could not get remote working options, reason: mocked-test-exception'}


