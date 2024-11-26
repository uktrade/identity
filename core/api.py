from typing import List

from ninja import Router

from .schemas.scim_schema import SCIMUser, user
from .services.user import UserService


router = Router()


@router.get("scim/v2/Users", response=List[SCIMUser])
def get_users(request):
    users = user.objects.all()
    return users


@router.post("scim/v2/Users", response=SCIMUser)
def create_user(request, scim_request: SCIMUser):
    user, created = UserService.createUser(scim_request)

    if created:
        return 201, user
    else:
        return 200, user
