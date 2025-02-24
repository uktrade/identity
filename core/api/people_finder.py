from ninja import Router

from core import services as core_services
from core.schemas import Error
from core.schemas.profiles import ProfileMinimal, UkStaffLocationSchema
from profiles.models.combined import Profile
from profiles.models.generic import UkStaffLocation
from profiles.models.peoplefinder import PeopleFinderProfile
from profiles.services import peoplefinder


router = Router()
profile_router = Router()
uk_location_router = Router()
router.add_router("person", profile_router)
router.add_router("uk-location", uk_location_router)


# NB this is a placeholder to get the router running, it may need editing or deleting etc.
@profile_router.get(
    "{id}",
    response={
        200: ProfileMinimal,
        404: Error,
    },
)
def get_user(request, id: str):
    """Just a demo, do not build against this"""
    try:
        return core_services.get_identity_by_id(id=id)
    except Profile.DoesNotExist:
        return 404, {
            "message": "Unable to find user",
        }

@uk_location_router.get(
    "{id}",
    response={
        200: UkStaffLocationSchema,
        404: Error,
    }
)
def get_uk_staff_location(request, slug: str) -> tuple[int, UkStaffLocation | dict]:
    try:
        # Use get by slug from core
        profile = peoplefinder.get_by_slug(slug=slug)
        location = profile.uk_office_location.__dict__
        return 200, location
    except PeopleFinderProfile.DoesNotExist:
        return 404, {
            "message": "People finder profile does not exist",
        }
    except AttributeError:
        return 404, {
            "message": "Uk staff location is not set for the people finder profile",
        }