from typing import List

from django.contrib.auth import get_user_model
from ninja import Router

from core.service import CoreService
from scim.service import SCIMService

from .schema import SCIMUser


User = get_user_model()
router = Router()
scim_service = SCIMService()


@router.get("scim/v2/Users/{id}", response=SCIMUser)
def get_user(request, id: str):
    return scim_service.get_user_by_id(id)


response_codes = frozenset({200, 201})


@router.post("scim/v2/Users", response={response_codes: SCIMUser})
def create_user(request, scim_user: SCIMUser):
    user, created = scim_service.get_or_create_user(scim_user)
    if created:
        return 201, user
    else:
        return 200, user
