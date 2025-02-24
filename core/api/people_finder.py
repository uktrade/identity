from ninja import Router

from core import services as core_services
from core.schemas import Error
from core.schemas.peoplefinder import MinimalPeopleFinderProfile
from profiles.models import PeopleFinderProfile


router = Router()
profile_router = Router()
router.add_router("person", profile_router)


@profile_router.get(
    "{slug}",
    response={
        200: MinimalPeopleFinderProfile,
        404: Error,
    },
)
def get_profile(request, slug: str):
    """Optimised, low-flexibility endpoint to return a minimal peoplefinder profile record"""
    try:
        return core_services.get_peoplefinder_profile_by_slug(slug=slug)
    except PeopleFinderProfile.DoesNotExist:
        return 404, {
            "message": "Unable to find people finder profile",
        }
