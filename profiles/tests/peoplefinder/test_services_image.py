from re import T

import pytest

from profiles import types
from profiles.services import image


pytestmark = pytest.mark.django_db


def test_get_standard_profile_photo(mocker):
    profile = mocker.Mock()
    profile.photo = False
    mock_svc = mocker.patch("profiles.services.image.peoplefinder_profile_services")
    mock_svc.get_by_slug.return_value = profile
    mock_get_dims = mocker.patch(
        "profiles.services.image.get_dimensions_and_prefix_from_standard_size",
        return_value=("--size--", "--prefix--"),
    )
    mock_get_or_create = mocker.patch(
        "profiles.services.image.get_or_create_sized_image"
    )

    assert (
        image.get_standard_profile_photo("SLUG", types.ImageStandardSizes.MAIN) == None
    )
    mock_get_dims.assert_not_called()
    mock_get_or_create.assert_not_called()

    profile.photo = mocker.Mock()
    assert (
        image.get_standard_profile_photo("SLUG", types.ImageStandardSizes.MAIN)
        == mock_get_or_create.return_value
    )
    mock_get_dims.assert_called_once_with(types.ImageStandardSizes.MAIN)
    mock_get_or_create.assert_called_once_with(
        profile.photo.name, "--size--", "--prefix--"
    )

    mock_get_dims.reset_mock()
    image.get_standard_profile_photo("SLUG", types.ImageStandardSizes.THUMBNAIL)
    mock_get_dims.assert_called_once_with(types.ImageStandardSizes.THUMBNAIL)


def test_get_main_profile_photo(mocker):
    mock_std_profile = mocker.patch(
        "profiles.services.image.get_standard_profile_photo"
    )
    image.get_main_profile_photo(slug="a-slug")
    mock_std_profile.assert_called_once_with(
        slug="a-slug", standard_size=types.ImageStandardSizes.MAIN
    )


def test_get_small_profile_photo(mocker):
    mock_std_profile = mocker.patch(
        "profiles.services.image.get_standard_profile_photo"
    )
    image.get_small_profile_photo(slug="a-slug")
    mock_std_profile.assert_called_once_with(
        slug="a-slug", standard_size=types.ImageStandardSizes.SMALL
    )


def test_get_thumbnail_profile_photo(mocker):
    mock_std_profile = mocker.patch(
        "profiles.services.image.get_standard_profile_photo"
    )
    image.get_thumbnail_profile_photo(slug="a-slug")
    mock_std_profile.assert_called_once_with(
        slug="a-slug", standard_size=types.ImageStandardSizes.THUMBNAIL
    )
