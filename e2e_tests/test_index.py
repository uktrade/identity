import pytest
from django.urls import reverse


pytestmark = [pytest.mark.django_db, pytest.mark.e2e,]


def test_authorised_access(state):
    url = reverse("core:index")
    response = state.client.get(url)

    assert response.status_code == 200
    assert b"Identity Service" in response.content


def test_superuser_access(state):
    user = state.user
    user.is_superuser = True
    user.save()

    url = reverse("core:index")
    response = state.client.get(url)

    assert response.status_code == 200
    assert b"Identity Service" in response.content
