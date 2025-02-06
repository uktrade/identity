from ninja import Router

from core import services as core_services
from core.schemas import Error
from core.schemas.profiles import ProfileMinimal
from profiles.models.combined import Profile


router = Router()


@router.get(
    "{id}",
    response={
        200: ProfileMinimal,
        404: Error,
    },
)
def get_user(request, id: str):
    """Optimised, low-flexibility endpoint to return a minimal Identity record (internally: Profile)"""
    try:
        return core_services.get_active_profile_by_id(id)
    except Profile.DoesNotExist:
        return 404, {
            "message": "Unable to find user",
        }
