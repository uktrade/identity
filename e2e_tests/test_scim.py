import json

import pytest
from django.test.client import Client
from django.urls import reverse

from core import services
from profiles.models.combined import Profile


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.e2e,
]


def test_create(scim_user_factory):
    client = Client()
    scim_user = scim_user_factory()
    scim_user_dict = json.loads(scim_user)
    url = reverse("scim:create_user")

    with pytest.raises(Profile.DoesNotExist):
        services.get_profile_by_id(scim_user_dict["id"], include_inactive=True)

    response = client.post(
        url,
        data=scim_user,
        content_type="application/json",
    )

    assert response.status_code == 201
    profile = services.get_profile_by_id(scim_user_dict["id"], include_inactive=True)
    assert profile.first_name == scim_user_dict["name"]["givenName"]
    assert profile.last_name == scim_user_dict["name"]["familyName"]
    assert len(profile.emails) == len(scim_user_dict["emails"])
    for scim_email in scim_user_dict["emails"]:
        assert scim_email["value"] in profile.emails
        if scim_email["primary"]:
            assert profile.primary_email == scim_email["value"]
        if scim_email["type"] == "contact":
            assert profile.contact_email == scim_email["value"]

    response = client.post(
        url,
        data=scim_user,
        content_type="application/json",
    )
    assert response.status_code == 409

    no_email = scim_user_dict
    no_email["emails"] = []
    scim_no_email = json.dumps(no_email)

    response = client.post(
        url,
        data=scim_no_email,
        content_type="application/json",
    )
    assert response.status_code == 400

    inactive = scim_user_dict
    inactive["is_active"] = False
    scim_inactive = json.dumps(inactive)

    response = client.post(
        url,
        data=scim_inactive,
        content_type="application/json",
    )
    assert response.status_code == 400
