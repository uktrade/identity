import json
import uuid

import pytest
from django.test.client import Client
from django.urls import reverse

from core.schemas.peoplefinder import CreateProfileRequest
from profiles.models import LearningInterest, Workday
from profiles.models.peoplefinder import RemoteWorking


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.e2e,
]


def test_get_profile(peoplefinder_profile):
    client = Client()
    url = reverse("people-finder:get_profile", args=(str(peoplefinder_profile.slug),))

    response = client.get(
        url,
        content_type="application/json",
    )
    # Returns a positive response
    assert response.status_code == 200

    profile_response = response.json()

    # Returned fields match peoplefinder profile
    assert peoplefinder_profile.first_name == profile_response["first_name"]
    assert peoplefinder_profile.last_name == profile_response["last_name"]
    assert peoplefinder_profile.user.sso_email_id == profile_response["sso_email_id"]
    assert (
        peoplefinder_profile.preferred_first_name
        == profile_response["preferred_first_name"]
    )
    assert (
        peoplefinder_profile.name_pronunciation
        == profile_response["name_pronunciation"]
    )
    assert (
        peoplefinder_profile.primary_phone_number
        == profile_response["primary_phone_number"]
    )
    assert peoplefinder_profile.photo == profile_response["photo"]
    assert peoplefinder_profile.photo_small == profile_response["photo_small"]
    assert peoplefinder_profile.grade == profile_response["grade"]

    url = reverse("people-finder:get_profile", args=(str(uuid.uuid4()),))

    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 404


def test_create(combined_profile):
    client = Client()
    url = reverse("people-finder:create_profile")
    test_uuid = str(uuid.uuid4())
    test_profile = CreateProfileRequest(
        slug=test_uuid, sso_email_id=combined_profile.sso_email_id
    )

    # Create a new PF Profile
    response = client.post(
        url, data=test_profile.model_dump_json(), content_type="application/json"
    )

    # Profile creation returns 201 CREATED
    assert response.status_code == 201
    profile_response = response.json()

    # Profile input values match returned values
    assert profile_response["sso_email_id"] == test_profile.sso_email_id
    assert profile_response["slug"] == test_profile.slug
    assert profile_response["login_count"] == test_profile.login_count
    assert profile_response["country_id"] == test_profile.country_id

    # Send a duplicate PF Profile request
    response = client.post(
        url, data=test_profile.model_dump_json(), content_type="application/json"
    )

    assert response.status_code == 409

    # Send a bad request
    bad_request = {"sso_email_id": "Bad Request"}
    response = client.post(
        url, data=json.dumps(bad_request), content_type="application/json"
    )

    assert response.status_code == 422
    response_json = response.json()
    assert response_json == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "profile_request", "slug"],
                "msg": "Field required",
            }
        ]
    }


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
            "split": "SPLIT",
        },
    )

    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {
        "message": "Could not get remote working options, reason: too many values to unpack (expected 2)"
    }

    mocker.patch(
        "core.services.get_remote_working",
        side_effect=Exception("mocked-test-exception"),
    )

    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {
        "message": "Could not get remote working options, reason: mocked-test-exception"
    }


def test_get_workday(mocker):
    url = reverse("people-finder:get_workdays")
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
        "core.services.get_workdays",
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
        "core.services.get_workdays", side_effect=Exception("mocked-test-exception")
    )
    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {
        "message": "Could not get workday options, reason: mocked-test-exception"
    }


def test_get_learning_interest(mocker):
    url = reverse("people-finder:get_learning_interests")
    client = Client()
    response = client.get(
        url,
        content_type="application/json",
    )
    assert response.status_code == 200
    assert json.loads(response.content) == [
        {"key": key, "value": value} for key, value in LearningInterest.choices
    ]

    mocker.patch(
        "core.services.get_learning_interests",
        return_value={
            "Work shadowing": "Shadowing",
            "Mentoring": "Mentoring",
            "Research": "Research",
            "Overseas posts": "Overseas Posts",
            "Secondment": "Secondment",
            "Parliamentary work": "Parliamentary Work",
            "Ministerial submissions": "Ministerial Submissions",
            "Coding": "Coding",
        },
    )

    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {
        "message": "Could not get learning interest options, reason: too many values to unpack (expected 2)"
    }

    mocker.patch(
        "core.services.get_learning_interests",
        side_effect=Exception("mocked-test-exception"),
    )
    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {
        "message": "Could not get learning interest options, reason: mocked-test-exception"
    }
