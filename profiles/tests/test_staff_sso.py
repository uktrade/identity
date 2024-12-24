import pytest
from django.test import TestCase

from profiles.models import TYPES, Email, StaffSSOProfile, StaffSSOProfileEmail
from profiles.services import staff_sso as staff_sso_service
from user.models import User


class StaffSSOServiceTest(TestCase):

    @pytest.mark.django_db
    def setUp(self):
        # Create a user for use in the tests
        self.user, _ = User.objects.get_or_create(
            sso_email_id="email@email.com",
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )

        self.first_name = "John"
        self.last_name = "Doe"
        self.emails = [
            {
                "address": "email1@email.com",
                "type": TYPES[0][0],
                "preferred": False,
            },
            {"address": "email2@email.com", "type": TYPES[1][0], "preferred": True},
        ]

    @pytest.mark.django_db
    def test_get_or_create_staff_sso_profile(self):

        staff_sso_profile, created = staff_sso_service.get_or_create_staff_sso_profile(
            user=self.user,
            first_name=self.first_name,
            last_name=self.last_name,
            emails=self.emails,
        )

        self.assertTrue(created)
        # assert 2 email records created
        self.assertEqual(Email.objects.all().count(), 2)
        self.assertEqual(Email.objects.first().address, "email1@email.com")
        self.assertEqual(Email.objects.last().address, "email2@email.com")

        # assert staff sso profile created
        self.assertEqual(StaffSSOProfile.objects.all().count(), 1)
        self.assertEqual(StaffSSOProfile.objects.first().first_name, "John")
        self.assertEqual(StaffSSOProfile.objects.first().last_name, "Doe")
        self.assertEqual(
            StaffSSOProfile.objects.first().user.sso_email_id, "email@email.com"
        )

        # assert staff sso email created
        self.assertEqual(StaffSSOProfileEmail.objects.all().count(), 2)
        self.assertEqual(
            StaffSSOProfileEmail.objects.first().email.address, "email1@email.com"
        )
        self.assertEqual(StaffSSOProfileEmail.objects.first().type, "work")
        self.assertEqual(StaffSSOProfileEmail.objects.first().preferred, False)
        self.assertEqual(
            StaffSSOProfileEmail.objects.last().email.address, "email2@email.com"
        )
        self.assertEqual(StaffSSOProfileEmail.objects.last().type, "contact")
        self.assertEqual(StaffSSOProfileEmail.objects.last().preferred, True)
        self.assertEqual(
            StaffSSOProfileEmail.objects.first().profile.first_name, "John"
        )
        self.assertEqual(StaffSSOProfileEmail.objects.first().profile.last_name, "Doe")
        self.assertEqual(StaffSSOProfileEmail.objects.last().profile.first_name, "John")
        self.assertEqual(StaffSSOProfileEmail.objects.last().profile.last_name, "Doe")

    def test_get_staff_sso_profile_by_id(self):
        staff_sso_profile, created = staff_sso_service.get_or_create_staff_sso_profile(
            user=self.user,
            first_name=self.first_name,
            last_name=self.last_name,
            emails=self.emails,
        )
        actual = staff_sso_service.get_staff_sso_profile_by_id(staff_sso_profile.id)
        self.assertTrue(created)
        self.assertEqual(actual.user.sso_email_id, "email@email.com")
        self.assertEqual(actual.first_name, "John")
        self.assertEqual(actual.last_name, "Doe")

    @pytest.mark.django_db
    def test_update_staff_sso_profile(self):
        staff_sso_profile, created = staff_sso_service.get_or_create_staff_sso_profile(
            user=self.user,
            first_name=self.first_name,
            last_name=self.last_name,
            emails=self.emails,
        )
        kwargs = {
            "first_name": "newTom",
            "last_name": "newJones",
        }
        emails = [
            {"address": "email2@email.com", "type": TYPES[1][0], "preferred": False}
        ]

        # check values before update
        staff_sso_email = StaffSSOProfileEmail.objects.filter(
            email=Email.objects.get(address="email2@email.com")
        )[0]
        self.assertTrue(staff_sso_email.preferred)
        self.assertEqual(staff_sso_profile.first_name, self.first_name)
        self.assertEqual(staff_sso_profile.last_name, self.last_name)

        updated_staff_sso_profile = staff_sso_service.update_staff_sso_profile(
            id=staff_sso_profile.id, emails=emails, **kwargs
        )

        self.assertEqual(updated_staff_sso_profile.first_name, "newTom")
        self.assertEqual(updated_staff_sso_profile.last_name, "newJones")
        staff_sso_email = StaffSSOProfileEmail.objects.filter(
            email=Email.objects.get(address="email2@email.com")
        )[0]
        self.assertFalse(staff_sso_email.preferred)
