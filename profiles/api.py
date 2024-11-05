from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.security import HttpBearer, django_auth

import profiles.models.people_finder as pf
from user.models.models import User

from .schema import PeopleProfileIn, PeopleProfileOut


router = Router()


class AuthProfile(HttpBearer):
    def authenticate(self, request, token):
        if token == "profilesecret":
            return token


@router.post("/add", response=PeopleProfileOut)
def add_profile(request, data: PeopleProfileIn):
    profile = pf.PeopleFinderProfile.objects.create(
        user=User.objects.filter(username=data.username).first(),
        fav_program=data.fav_program,
        super_important=data.super_important,
    )
    return profile


@router.get("/{id}", response=PeopleProfileOut)
def get_employee(request, id: int):
    profile = get_object_or_404(pf.PeopleFinderProfile, id=id)
    return profile


@router.get("/add", response=List[PeopleProfileOut])  # auth=AuthProfile()
def show_profiles(request):
    profiles = pf.PeopleFinderProfile.objects.all()
    return profiles
    # profiles = list(pf.PeopleFinderProfile.objects.all())
    # return {
    #     "profiles": [
    #         {
    #             "id": profile.id,
    #             "profile": profile.user.username,
    #             "fav_program": profile.fav_program,
    #             "super_important": profile.super_important
    #         }
    #         for profile in profiles
    #     ]
    # }
