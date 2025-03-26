import pytest
from django.core.files import File
from django.test.client import Client
from django.urls import reverse


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.e2e,
]


def test_photo_only_authorised_access(peoplefinder_profile):
    client = Client()
    url = reverse("core:photo", args=( peoplefinder_profile.slug,))
    response = client.get(url)

    assert response.status_code == 302

    client.force_login(peoplefinder_profile.user)
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.content) == 0  # no photo exists

    local_file = open('docker/.localstack/fixtures/photo.jpg', 'rb')
    djangofile = File(local_file)
    peoplefinder_profile.photo.save('new', djangofile)
    local_file.close()

    response = client.get(url)
    assert response.status_code == 200
    assert len(response.content) == djangofile.size
