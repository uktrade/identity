import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_index_view(client):
    url = reverse("core:index")
    response = client.get(url)

    assert response.status_code == 302
    # assert b"Identity Service" in response.content
