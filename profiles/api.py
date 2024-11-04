from ninja import Router
from ninja.security import HttpBearer, django_auth

import profiles.models.people_finder as pf
from user.models.models import User


router = Router()


@router.post("add-user/")
def add_user(request, username: str):
    user = User.objects.create_user(username=username)
    return {"user": user.username}


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if token == "supersecret":
            return token


@router.get("/show-users", auth=AuthBearer())
def show_users(request):
    users = User.objects.all()
    return {"users": [{"id": user.id, "username": user.username} for user in users]}


@router.post("add-profile")
def add_profile(request, username: str):
    profile = pf.PeopleFinderProfile.objects.create(
        user=User.objects.filter(username=username).first()
    )
    return {"profile": profile.user.username}


@router.get("/show-profiles")
def show_profiles(request):
    profiles = list(pf.PeopleFinderProfile.objects.all())
    return {
        "profiles": [
            {"id": profile.id, "profile": profile.user.username} for profile in profiles
        ]
    }
