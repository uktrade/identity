from ninja import Router

from core import services as core_services
from core.schemas import Error
from profiles.models.combined import Profile
from profiles.schemas import ProfileMinimal


router = Router()


@router.get(
    "{id}",
    response={
        200: ProfileMinimal,
        404: Error,
    },
)
def get_user(request, id: str):
    """In fact returns the combined Profile"""
    try:
        return core_services.get_by_id(id)
    except Profile.DoesNotExist:
        return 404, {
            "message": "Unable to find user",
        }
