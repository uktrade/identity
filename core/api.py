from typing import List

from identity.core.models import Proifle, StaffSSOProfile
from ninja import Router

from .schemas.scim_schema import SCIMUser, user
from .services.user import UserService


router = Router()


@router.get("scim/v2/Users", response=List[SCIMUser])
def get_users(request):
    users = user.objects.all()
    return users


responsecodes = frozenset({200, 201})


@router.get("/user/emails?profile=peoplefinder")
def get_emails(request):
    emails = CoreService.get_user_emails(request)
    return emails

@router.post("scim/v2/Users", response={responsecodes: SCIMUser})
def create_user(request, scim_request: SCIMUser):
    user, created = CoreService.createUser(scim_request)
    # user, created = UserService.createUser(scim_request)

    if created:
        return 201, user
    else:
        return 200, user


class CoreService:
   def create_user(scim_request):
        user = UserService.createUser(scim_request)


        request = {

        }


        profile = ProfileService.createProfile(request, StaffSSOProfile)

   def create_profile(request):
       
        request = {

        }
        ProfileService.createProfile(request)

class ProfileService:
    def get_profile(str) -> Proifle:
        return StaffSSOProfile

    def create_profile(self,request, type):
        profileType = self.get_profile(type)
        
        profile, created =  profileType.objects.get_or_create(request)
