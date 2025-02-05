from ninja import Router

from core import services as core_services
from core.schemas import Error
from core.schemas.peoplefinder import PeopleFinderProfileSchema
from profiles.models.peoplefinder import PeopleFinderProfile


router = Router()
profile_router = Router()
router.add_router("person", profile_router)


# NB this is a placeholder to get the router running, it may need editing or deleting etc.
@profile_router.get(
    "{id}",
    response={
        200: PeopleFinderProfileSchema,
        404: Error,
    },
)
def get_people_finder_profile(request, id: str):
    """Just a demo, do not build against this - still incomplete"""
    try:
        return core_services.get_by_id(id)
    except PeopleFinderProfile.DoesNotExist:
        return 404, {
            "message": "Unable to find user",
        }
