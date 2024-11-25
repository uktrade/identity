from .schemas.scim_schema import SCIMRequest, user
from ninja import Router

router = Router()

@router.get("/Users", response=SCIMRequest)
def get_users(request):



    users = user.objects.first()
    return users


