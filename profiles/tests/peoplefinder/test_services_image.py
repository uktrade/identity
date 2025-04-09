import pytest

from profiles import types
from profiles.services import image

pytestmark = pytest.mark.django_db


def test_get_standard_profile_photo():
    assert False


def test_get_main_profile_photo(mocker):
    mock_std_profile = mocker.patch("profiles.services.image.get_standard_profile_photo")
    image.get_main_profile_photo(slug="a-slug")
    mock_std_profile.assert_called_once_with(slug="a-slug", standard_size=types.ImageStandardSizes.MAIN)


def test_get_small_profile_photo(mocker):
    mock_std_profile = mocker.patch("profiles.services.image.get_standard_profile_photo")
    image.get_small_profile_photo(slug="a-slug")
    mock_std_profile.assert_called_once_with(slug="a-slug", standard_size=types.ImageStandardSizes.SMALL)


def test_get_thumbnail_profile_photo(mocker):
    mock_std_profile = mocker.patch("profiles.services.image.get_standard_profile_photo")
    image.get_thumbnail_profile_photo(slug="a-slug")
    mock_std_profile.assert_called_once_with(slug="a-slug", standard_size=types.ImageStandardSizes.THUMBNAIL)
