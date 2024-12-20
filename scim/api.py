from ninja import Router

from core import services as core_service
from profiles import services as profile_service

from .schemas import SCIMUserIn, SCIMUserOut


router = Router()


@router.get("scim/v2/Users/{id}", response=SCIMUserOut)
def get_user(request, id: str):
    return profile_service.combined.get_by_id(id)


response_codes = frozenset({200, 201})


@router.post("scim/v2/Users", response={response_codes: SCIMUserOut})
def create_user(request, scim_user: SCIMUserIn):
    # @TODO fix mypy stuff properly
    user = core_service.create_user(  # type: ignore
        scim_user.id, "SSO", **scim_user  # type: ignore
    )  # type: ignore
    # if created:
    return 201, user
    # else:
    #     return 200, user
