from typing import List

from django.contrib.auth import get_user_model
from ninja import Router

from .schemas.scim_schema import SCIMUser


user_model = get_user_model()

router = Router()


@router.get("scim/v2/Users", response=List[SCIMUser])
def get_users(request):
    users = user_model.objects.all()
    return users


@router.post("scim/v2/Users")
def create_user(request, scim_request: SCIMUser):
    user, created = user_model.objects.get_or_create(scim_request)
    if created:
        return 201, user
    else:
        return 200, user
