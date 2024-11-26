from typing import List

from ninja import Router

from core.services.scim import SCIMService

from .schemas.scim_schema import Name, SCIMRequest, user


router = Router()


@router.get("scim/v2/Users", response=List[SCIMRequest])
def get_users(request):
    users = user.objects.all()
    # SCIMService.transform_user()
    return users

    # for u in users:
    #     names = {"familyName": u.last_name,"givenName": u.first_name}
    #     return {
    #         # "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
    #         "userName": u.username,
    #         "name": names,
    #         "emails": u.email,
    #         "active": u.is_active,
    #     }


@router.post("scim/v2/Users")
def create_user(request, scim_request: SCIMRequest):
    user = SCIMService.transform_user(scim_request)
    response = SCIMService.to_scim(user)
    return response
