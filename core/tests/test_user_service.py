import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

from core.schemas.scim_schema import Name, SCIMUser
from core.services.user_service import UserService


User = get_user_model()


class UserServiceTest(TestCase):

    @pytest.mark.django_db
    def setUp(self):
        self.user_service = UserService()
        # Create a user for use in the tests
        self.user = User.objects.create_user(
            username="testuser",
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )

    @pytest.mark.django_db
    def test_create_user(self):
        scim_user = SCIMUser(
            externalId="newuser",
            is_active=True,
            username="random_username",
            name=Name(
                givenName="givenname",
                familyName="familyname",
            ),
        )
        user, created = self.user_service.create_user(scim_user)
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_superuser, False)
        self.assertTrue(created)

    @pytest.mark.django_db
    def test_get_user(self):
        user = self.user_service.get_user(self.user.id)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_superuser, False)

    @pytest.mark.django_db
    def test_search_users(self):
        second_user = User.objects.create_user(
            username="testuser2",
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        users = self.user_service.search_users({"is_active": True, "is_staff": False})
        user = users[0]
        self.assertEqual(len(users), 2)
        self.assertEqual(users[1], second_user)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_superuser, False)

    @pytest.mark.django_db
    def test_update_user(self):
        scim_user = SCIMUser(
            externalId="updateduser",
            is_active=True,
            username="random_username",
            name=Name(
                givenName="givenname",
                familyName="familyname",
            ),
        )
        updated_user = self.user_service.update_user(self.user.id, scim_user=scim_user)
        self.assertEqual(updated_user.username, "updateduser")
        self.assertEqual(updated_user.is_active, True)
        self.assertEqual(updated_user.is_staff, False)
        self.assertEqual(updated_user.is_superuser, False)

    @pytest.mark.django_db
    def test_delete_user(self):
        deleted_user = self.user_service.delete_user(self.user.id)
        self.assertFalse(deleted_user.is_active)

        # Try to get a soft-deleted user
        self.assertIsNone(self.user_service.get_user(self.user.id))

    @pytest.mark.django_db
    def test_restore_user(self):
        # Soft delete the user first
        deleted_user = self.user_service.delete_user(self.user.id)
        # update the user setting active True
        scim_user = SCIMUser(
            externalId=deleted_user.username,
            is_active=True,
            username="random_username",
            name=Name(
                givenName="givenname",
                familyName="familyname",
            ),
        )

        restored_user = self.user_service.update_user(self.user.id, scim_user)
        self.assertTrue(restored_user.is_active)

        # Ensure we can access the restored user
        restored_user = self.user_service.get_user(self.user.id)
        self.assertEqual(restored_user.username, "testuser")

    @pytest.mark.django_db
    def test_user_not_found(self):
        self.assertIsNone(self.user_service.get_user(9999))

    @pytest.mark.django_db
    def test_search_users_empty_result(self):
        self.assertEqual(len(self.user_service.search_users({"id": 9999})), 0)

    @pytest.mark.django_db
    def test_user_update_not_found(self):
        scim_user = SCIMUser(
            externalId="newname",
            is_active=True,
            username="random_username",
            name=Name(
                givenName="givenname",
                familyName="familyname",
            ),
        )
        self.assertIsNone(self.user_service.update_user(9999, scim_user=scim_user))

    @pytest.mark.django_db
    def test_delete_not_found(self):
        self.assertIsNone(self.user_service.delete_user(9999))
