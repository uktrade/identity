import datetime as dt
import json
import os
import uuid

import pytest
from django.test.client import Client
from django.urls import reverse

from core.schemas.peoplefinder.profile import CreateProfileRequest, UpdateProfileRequest
from profiles.models import LearningInterest, Workday
from profiles.models.generic import Country, Grade, Profession, UkStaffLocation
from profiles.models.peoplefinder import (
    AdditionalRole,
    KeySkill,
    PeopleFinderTeam,
    RemoteWorking,
)


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
        slug=test_uuid,
        sso_email_id=combined_profile.sso_email_id,
        contact_email_address=combined_profile.contact_email,
        email_address=combined_profile.primary_email,
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
            },
        ],
    }


def test_update(combined_profile, peoplefinder_profile):
    client = Client()
    update_request = UpdateProfileRequest(
        sso_email_id=combined_profile.sso_email_id,
        first_name="Alison",
        last_name="Doe",
        email_address="alison.doe@example.com",
        contact_email_address="alison.doe@example_contact.com",
        grade=Grade("grade_7"),
        workdays=[Workday("mon"), Workday("tue")],
        professions=[Profession("commercial")],
        additional_roles=[AdditionalRole("fire_warden")],
        key_skills=[KeySkill("coaching")],
        learning_interests=[LearningInterest("shadowing")],
        edited_or_confirmed_at=dt.datetime.now(),
        preferred_first_name="Alison",
        became_inactive=None,
        login_count=0,
        pronouns=None,
        not_employee=False,
        name_pronunciation=None,
        primary_phone_number=None,
        secondary_phone_number=None,
        manager_slug=None,
        remote_working=None,
        usual_office_days=None,
        uk_office_location_id=None,
        location_in_building=None,
        international_building=None,
        country_id="CTHMTC00260",
        other_key_skills=None,
        other_learning_interests=None,
        fluent_languages=None,
        intermediate_languages=None,
        previous_experience=None,
        other_additional_roles=None,
    )
    url = reverse(
        "people-finder:update_profile", args=(str(peoplefinder_profile.slug),)
    )

    # Update an existing PF Profile
    response = client.put(
        url, data=update_request.model_dump_json(), content_type="application/json"
    )

    # Profile update returns 200 OK
    assert response.status_code == 200
    profile_response = response.json()

    # Profile input values match returned values
    assert profile_response["sso_email_id"] == update_request.sso_email_id
    assert profile_response["slug"] == peoplefinder_profile.slug
    assert profile_response["first_name"] == update_request.first_name

    # Try to update profile that doesn't exist
    wrong_uuid = str(uuid.uuid4())
    update_request = UpdateProfileRequest(
        sso_email_id=combined_profile.sso_email_id,
        first_name="Alison",
        last_name="Doe",
        email_address="alison.doe@example.com",
        contact_email_address="alison.doe@example_contact.com",
        grade=Grade("grade_7"),
        workdays=[Workday("mon"), Workday("tue")],
        professions=[Profession("commercial")],
        additional_roles=[AdditionalRole("fire_warden")],
        key_skills=[KeySkill("coaching")],
        learning_interests=[LearningInterest("shadowing")],
        edited_or_confirmed_at=dt.datetime.now(),
        preferred_first_name="Alison",
        became_inactive=None,
        login_count=0,
        pronouns=None,
        not_employee=False,
        name_pronunciation=None,
        primary_phone_number=None,
        secondary_phone_number=None,
        manager_slug=None,
        remote_working=None,
        usual_office_days=None,
        uk_office_location_id=None,
        location_in_building=None,
        international_building=None,
        country_id="CTHMTC00260",
        other_key_skills=None,
        other_learning_interests=None,
        fluent_languages=None,
        intermediate_languages=None,
        previous_experience=None,
        other_additional_roles=None,
    )
    url = reverse("people-finder:update_profile", args=(str(wrong_uuid),))

    response = client.put(
        url, data=update_request.model_dump_json(), content_type="application/json"
    )

    assert response.status_code == 404
    response_json = response.json()
    assert response_json == {"message": "People finder profile does not exist"}


def test_get_all_teams_hierarcy(mocker, peoplefinder_team):
    url = reverse("people-finder:get_hierarcy_of_all_teams")
    client = Client()
    response = client.get(
        url,
        content_type="application/json",
    )

    expected = {
        "slug": peoplefinder_team.slug,
        "name": peoplefinder_team.name,
        "abbreviation": peoplefinder_team.abbreviation,
        "children": [],
    }

    assert response.status_code == 200
    assert json.loads(response.content) == expected

    mocker.patch(
        "core.services.get_peoplefinder_team_hierarchy",
        side_effect=Exception("mocked-test-exception"),
    )

    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {
        "message": "Could not get the team hierarchy, reason: mocked-test-exception"
    }


def test_get_team(peoplefinder_team):
    url = reverse("people-finder:get_team", args=[peoplefinder_team.slug])
    client = Client()
    response = client.get(
        url,
        content_type="application/json",
    )

    expected = {
        "slug": peoplefinder_team.slug,
        "name": peoplefinder_team.name,
        "abbreviation": peoplefinder_team.abbreviation,
        "parents": [],
    }

    assert response.status_code == 200
    assert json.loads(response.content) == expected

    url = reverse("people-finder:get_team", args=["employee-experience"])
    client = Client()
    response = client.get(
        url,
        content_type="application/json",
    )
    assert response.status_code == 404
    assert json.loads(response.content) == {
        "message": "People finder team does not exist"
    }


def test_create_team(peoplefinder_team):
    url = reverse("people-finder:create_team")
    client = Client()

    # Test case 1) peoplefinder team is successfully created
    create_team_request = {
        "slug": "riverjack-squad",
        "name": "Riverjack",
        "abbreviation": "RJ",
        "description": "Riverjack squad works on Identity service.",
        "leaders_ordering": "alphabetical",
        "cost_code": "code1",
        "team_type": "standard",
        "parent_slug": peoplefinder_team.slug,
    }
    response = client.post(
        url,
        data=create_team_request,
        content_type="application/json",
    )
    expected = {
        "slug": "riverjack-squad",
        "name": "Riverjack",
        "abbreviation": "RJ",
    }
    assert response.status_code == 200
    assert json.loads(response.content) == expected

    # Test case 2) peoplefinder team already exists
    existing_team_request = {
        "slug": "riverjack-squad",
        "name": "Riverjack",
        "abbreviation": "RJ",
        "description": "Riverjack squad works on Identity service.",
        "leaders_ordering": "alphabetical",
        "cost_code": "code1",
        "team_type": "standard",
        "parent_slug": peoplefinder_team.slug,
    }

    response = client.post(
        url,
        data=existing_team_request,
        content_type="application/json",
    )
    assert response.status_code == 404
    assert json.loads(response.content) == {
        "message": "Team has been previously created"
    }

    # Test case 3) peoplefinder parent team does not exist
    non_existing_parent_team_request = {
        "slug": "new-team",
        "name": "New Team",
        "abbreviation": "New team",
        "description": "New team description",
        "leaders_ordering": "alphabetical",
        "cost_code": "code1",
        "team_type": "standard",
        "parent_slug": "not-in-db",
    }
    response = client.post(
        url,
        data=non_existing_parent_team_request,
        content_type="application/json",
    )
    assert response.status_code == 404
    assert json.loads(response.content) == {
        "message": "Cannot create the people finder team, parent team does not exist"
    }

    # Test parent team is not in the team hierarchy

    # We shouldn't have a peoplefinder team created through this method (except the root team)
    # If we use this method, team is not added to the team tree hierarchy
    PeopleFinderTeam.objects.create(slug="not-in-team-tree", name="Not in Team Tree")

    parent_not_in_hierarchy_request = {
        "slug": "identity-squad",
        "name": "Identity",
        "abbreviation": "ID",
        "description": "Identity squad works on Identity service.",
        "leaders_ordering": "alphabetical",
        "cost_code": "code1",
        "team_type": "standard",
        "parent_slug": "not-in-team-tree",
    }
    response = client.post(
        url,
        data=parent_not_in_hierarchy_request,
        content_type="application/json",
    )
    assert response.status_code == 404
    assert json.loads(response.content) == {
        "message": "Parent team is not in the team hierarchy"
    }


def test_upload_delete_photo(peoplefinder_profile):
    url = reverse(
        "people-finder:upload_profile_photo", args=(str(peoplefinder_profile.slug),)
    )
    filepath = "docker/.localstack/fixtures/photo.jpg"
    client = Client()

    with open(filepath, "rb") as file:
        response = client.post(
            url,
            data={"image": file},
        )
        assert response.status_code == 200
        peoplefinder_profile.refresh_from_db()
        assert peoplefinder_profile.photo.size == os.path.getsize(filepath)

    response = client.delete(url)
    assert response.status_code == 200
    peoplefinder_profile.refresh_from_db()
    assert bool(peoplefinder_profile.photo) is False

    filepath = "docker/.localstack/fixtures/staff_sso.jsonl"
    with open(filepath, "rb") as file:
        response = client.post(
            url,
            data={"image": file},
        )
        assert response.status_code == 422
        assert json.loads(response.content) == {"message": "Not a valid image file"}


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
        "message": "Could not get workdays, reason: too many values to unpack (expected 2)"
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
        "message": "Could not get workdays, reason: mocked-test-exception"
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
        "message": "Could not get learning interests, reason: too many values to unpack (expected 2)"
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
        "message": "Could not get learning interests, reason: mocked-test-exception"
    }


def test_get_professions(mocker):
    url = reverse("people-finder:get_professions")
    client = Client()
    response = client.get(
        url,
        content_type="application/json",
    )
    assert response.status_code == 200
    assert json.loads(response.content) == [
        {"key": key, "value": value} for key, value in Profession.choices
    ]

    mocker.patch(
        "core.services.get_professions",
        return_value={
            "COMMERCIAL": "Government commercial and contract management",
            "CORP_FINANCE": "Corporate finance profession",
            "COUNTER_FRAUD": "Counter-fraud standards and profession",
            "DIGITAL_DATA_TECH": "Digital, data and technology profession",
            "GOV_COMMS": "Government communication service",
        },
    )

    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {
        "message": "Could not get professions, reason: too many values to unpack (expected 2)"
    }

    mocker.patch(
        "core.services.get_professions", side_effect=Exception("mocked-test-exception")
    )
    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {
        "message": "Could not get professions, reason: mocked-test-exception"
    }


def test_get_grades(mocker):
    url = reverse("people-finder:get_grades")
    client = Client()
    response = client.get(
        url,
        content_type="application/json",
    )
    assert response.status_code == 200
    assert json.loads(response.content) == [
        {"key": key, "value": value} for key, value in Grade.choices
    ]

    mocker.patch(
        "core.services.get_grades",
        return_value={
            "fco_s1": "FCO S1",
        },
    )

    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {
        "message": "Could not get grades, reason: too many values to unpack (expected 2)"
    }

    mocker.patch(
        "core.services.get_grades", side_effect=Exception("mocked-test-exception")
    )
    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {
        "message": "Could not get grades, reason: mocked-test-exception"
    }


def test_get_key_skills(mocker):
    url = reverse("people-finder:get_key_skills")
    client = Client()
    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 200
    assert json.loads(response.content) == [
        {"key": key, "value": value} for key, value in KeySkill.choices
    ]

    mocker.patch(
        "core.services.get_key_skills",
        return_value={
            "asset_management": "Asset management",
            "assurance": "Assurance",
            "benefits_realisation": "Benefits realisation",
            "change_management": "Change management",
            "coaching": "Coaching",
        },
    )
    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {
        "message": "Could not get key skills, reason: too many values to unpack (expected 2)"
    }

    mocker.patch(
        "core.services.get_key_skills", side_effect=Exception("mocked-test-exception")
    )
    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {
        "message": "Could not get key skills, reason: mocked-test-exception"
    }


def test_get_additional_roles(mocker):
    url = reverse("people-finder:get_additional_roles")
    client = Client()
    response = client.get(
        url,
        content_type="application/json",
    )
    assert response.status_code == 200
    assert json.loads(response.content) == [
        {"key": key, "value": value} for key, value in AdditionalRole.choices
    ]

    mocker.patch(
        "core.services.get_additional_roles",
        return_value={
            "fire_warden": "Fire warden",
        },
    )

    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {
        "message": "Could not get additional roles, reason: too many values to unpack (expected 2)"
    }

    mocker.patch(
        "core.services.get_additional_roles",
        side_effect=Exception("mocked-test-exception"),
    )
    response = client.get(
        url,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert json.loads(response.content) == {
        "message": "Could not get additional roles, reason: mocked-test-exception"
    }
