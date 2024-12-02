from typing import Type

from profile.models import PeopleFinderProfile, Profile, StaffSSOProfile


class ProfileService:
    def create_profile(self, profile_request: dict, profile_type: Type[Profile]):
        if profile_type is StaffSSOProfile:
            # create staff sso profile
            self.create_staff_sso_profile(profile_request)
        elif profile_type is PeopleFinderProfile:
            # create people finder profile
            self.create_people_finder_profile(profile_request)
        else:
            raise Exception(f"Unsupported Profile Type: {profile_type}")

    def create_staff_sso_profile(self, profile_request):
        staff_sso_profile = StaffSSOProfile(**profile_request)
        staff_sso_profile.save()
        return staff_sso_profile

    def create_people_finder_profile(self, profile_request):
        people_finder_profile = PeopleFinderProfile(**profile_request)
        people_finder_profile.save()
        return people_finder_profile
