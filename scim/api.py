from ninja import Router

from scim import services as scim_services

from .schemas import SCIMUserIn, SCIMUserOut


router = Router()


@router.get("scim/v2/Users/{id}", response=SCIMUserOut)
def get_user(request, id: str):
    return scim_services.get_user_by_id(id)


response_codes = frozenset({200, 201})


@router.post("scim/v2/Users", response={response_codes: SCIMUserOut})
def create_user(request, scim_user: SCIMUserIn):
    user, created = scim_services.get_or_create_user(scim_user)
    if created:
        return 201, user
    else:
        return 200, user
