from dataclasses import dataclass

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.test.client import Client
from django.urls import reverse


@dataclass
class State:
    client: Client
    user: AbstractUser


@pytest.fixture()
def state(db):
    user, _ = get_user_model().objects.get_or_create(
        username="test_user", email="test_user"
    )
    user.save()
    client = Client()
    client.force_login(user)
    return State(client=client, user=user)


@pytest.mark.django_db
def test_authorised_access(state):
    url = reverse("core:index")
    response = state.client.get(url)

    assert response.status_code == 200
    assert b"Identity Service" in response.content


@pytest.mark.django_db
def test_superuser_access(state):
    user = state.user
    user.is_superuser = True
    user.save()

    url = reverse("core:index")
    response = state.client.get(url)

    assert response.status_code == 200
    assert b"Identity Service" in response.content
