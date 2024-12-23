from ninja import Router

from core import services as core_services
from core.schemas import Error
from profiles import services as profile_services
from profiles.models import PROFILE_TYPE_STAFF_SSO
from profiles.models.generic import Profile
from profiles.schemas import ProfileMinimal
from scim.schemas import SCIMUserIn
from user.exceptions import UserAlreadyExists

router = Router()


@router.get(
    "scim/v2/Users/{id}",
    response={
        200: ProfileMinimal,
        404: Error,
    },
)
# @TODO check if we actually need this method, if not let's drop it or move out of SCIM
def get_user(request, id: str):
    try:
        return profile_services.combined.get_by_id(id)
    except Profile.DoesNotExist:
        return 404, {"message": "No user found with that ID"}


@router.post("scim/v2/Users", response={201: ProfileMinimal, 409: Error})
def create_user(request, scim_user: SCIMUserIn):
    try:
        user = core_services.create_user(
            scim_user.externalId,
            PROFILE_TYPE_STAFF_SSO,
            first_name=scim_user.name,
            last_name=scim_user.name,  # @TODO do we get the names split out?
            emails=scim_user.emails,
            preferred_email=scim_user.get_primary_email(),
        )
        return 201, user
    except UserAlreadyExists:
        return 409, {"message": "A user with that ID already exists"}
