from profiles.services import peoplefinder_profile_services
from profiles.types import ImageStandardSizes
from profiles.utils import (
    get_dimensions_and_prefix_from_standard_size,
    get_or_create_sized_image,
)


def get_standard_profile_photo(slug: str, standard_size: ImageStandardSizes):
    profile: peoplefinder_profile_services.PeopleFinderProfile = (
        peoplefinder_profile_services.get_by_slug(slug=slug, include_inactive=True)
    )
    if not bool(profile.photo):
        return None

    size, prefix = get_dimensions_and_prefix_from_standard_size(standard_size)

    return get_or_create_sized_image(profile.photo.name, size, prefix)


def get_main_profile_photo(slug: str):
    return get_standard_profile_photo(slug=slug, standard_size=ImageStandardSizes.MAIN)


def get_small_profile_photo(slug: str):
    return get_standard_profile_photo(slug=slug, standard_size=ImageStandardSizes.SMALL)


def get_thumbnail_profile_photo(slug: str):
    return get_standard_profile_photo(
        slug=slug, standard_size=ImageStandardSizes.THUMBNAIL
    )
