from typing import List


from ninja import Router

from core.services.core import CoreService

from .schemas.scim_schema import SCIMUser


router = Router()


@router.get("scim/v2/Users", response=List[SCIMUser])
def get_users(request):
    return CoreService.get_users()

responsecodes = frozenset({200, 201})
@router.post("scim/v2/Users", response={responsecodes: SCIMUser})
def create_user(request, scim_request: SCIMUser):
    return CoreService.create_user(scim_request)
