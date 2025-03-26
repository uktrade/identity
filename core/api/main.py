from ninja import Router

from core import services as core_services
from core.schemas import Error
from core.schemas.profiles import ProfileMinimal
from profiles.models.combined import Profile


router = Router()
identity_router = Router()
router.add_router("identities", identity_router)


# NB this is a placeholder to get the router running, it may need editing or deleting etc.
@identity_router.get(
    "{id}",
    response={
        200: ProfileMinimal,
        404: Error,
    },
)
def get_user(request, id: str):
    """Just a demo, do not build against this."""
    try:
        return core_services.get_identity_by_id(id=id)
    except Profile.DoesNotExist:
        return 404, {
            "message": "Unable to find user",
        }
