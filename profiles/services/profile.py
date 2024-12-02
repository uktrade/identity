# from typing import Type
#
# from django.contrib.postgres.fields import ArrayField
# from django.db.models import JSONField, EmailField
#
# from profiles.models import PeopleFinderProfile, Profile, StaffSSOProfile
#
#
# class ProfileService:
#     def create_profile(self, profile_request: dict, profile_type: Type[Profile]):
#         if profile_type is StaffSSOProfile:
#             # create staff sso profiles
#             self.create_staff_sso_profile(profile_request)
#         elif profile_type is PeopleFinderProfile:
#             # create people finder profiles
#             self.create_people_finder_profile(profile_request)
#         else:
#             raise Exception(f"Unsupported Profile Type: {profile_type}")
#
#     def create_staff_sso_profile(self, profile_request) -> tuple[StaffSSOProfile, bool]:
#         """
#         Create a new user with the specified username.
#         """
#         staff_sso_profile, created = StaffSSOProfile.objects.get_or_create(
#             user=profile_request["user"],
#             sso_id=profile_request["sso_id"],
#             given_name=profile_request["given_name"],
#             family_name=profile_request["family_name"],
#             preferred_email=EmailField(profile_request["preferred_email"]),
#             emails=[EmailField(email) for email in profile_request["emails"]],
#         )
#
#         return staff_sso_profile, created
#
#     def create_people_finder_profile(self, profile_request):
#         people_finder_profile = PeopleFinderProfile(**profile_request)
#         people_finder_profile.save()
#         return people_finder_profile
