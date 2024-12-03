from profiles.models import PeopleFinderProfile, Profile, StaffSSOProfile
from typing import Type

from django.contrib.auth.base_user import BaseUserManager


class ProfileService:
    def __init__(self):
        self.user_manager = BaseUserManager()

    def create_profile(self, profile_request: dict, profile_type: Type[Profile]):
        if profile_type is StaffSSOProfile:
            # create staff sso profiles
            self.create_staff_sso_profile(profile_request)
        elif profile_type is PeopleFinderProfile:
            # create people finder profiles
            self.create_people_finder_profile(profile_request)
        else:
            raise Exception(f"Unsupported Profile Type: {profile_type}")

    def create_staff_sso_profile(self, profile_request) -> tuple[StaffSSOProfile, bool]:
        """
        Create a new staff sso profile for the specified request.
        """
        staff_sso_profile, created = StaffSSOProfile.objects.get_or_create(
            user=profile_request["user"],
            sso_id=profile_request["sso_id"],
            given_name=profile_request["given_name"],
            family_name=profile_request["family_name"],
            preferred_email=self.user_manager.normalize_email(
                profile_request["preferred_email"]
            ),
            emails=[
                self.user_manager.normalize_email(email)
                for email in profile_request["emails"]
            ],
        )

        return staff_sso_profile, created

    def create_people_finder_profile(self, profile_request):
        """
        Create a new people finder profile for the specified request.
        """
        people_finder_profile, created = PeopleFinderProfile.objects.get_or_create(
            user=profile_request["user"],
            first_name=profile_request["first_name"],
            last_name=profile_request["last_name"],
            preferred_email=self.user_manager.normalize_email(
                profile_request["preferred_email"]
            ),
            emails=[
                self.user_manager.normalize_email(email)
                for email in profile_request["emails"]
            ],
        )

        return people_finder_profile, created
