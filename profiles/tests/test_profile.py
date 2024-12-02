# import pytest
# from django.contrib.auth import get_user_model
# from django.test import TestCase
#
# from core.schemas.scim_schema import Name, SCIMUser
# from profiles.services.profile import ProfileService
#
#
# User = get_user_model()
#
#
# class ProfileServiceTest(TestCase):
#
#     @pytest.mark.django_db
#     def setUp(self):
#         self.profile_service = ProfileService()
#         # Create a user for use in the tests
#         self.user = User.objects.create_user(
#             username="testuser",
#             is_active=True,
#             is_staff=False,
#             is_superuser=False,
#         )
#
#     @pytest.mark.django_db
#     def test_create_staff_sso_profile(self):
#         profile_request = {
#             "user": self.user,
#             "sso_id": 1234,
#             "given_name": "John",
#             "family_name": "Doe",
#             "preferred_email": "john.doe@email.com",
#             "emails": [
#                 "john.doe@email.com",
#                 "john.doe1@email.com",
#                 "john.doe2@email.com",
#             ]
#
#         }
#         staff_sso_profile, created = self.profile_service.create_staff_sso_profile(profile_request)
#         self.assertTrue(created)
#         self.assertEqual(staff_sso_profile.user.username, "testuser")
#         self.assertEqual(staff_sso_profile.sso_id, "some-sso-id")
#         self.assertEqual(staff_sso_profile.given_name, "John")
#         self.assertEqual(staff_sso_profile.family_name, "Doe")
