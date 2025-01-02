from typing import Literal

import pytest
from django.test import TestCase

from profiles.models.generic import Email, EmailTypes
from profiles.models.staff_sso import StaffSSOProfile, StaffSSOProfileEmail
from profiles.services import staff_sso as staff_sso_services
from user.models import User


class StaffSSOServiceTest(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.sso_email_id = "email@email.com"
        # Create a user for use in the tests
        self.user, _ = User.objects.get_or_create(
            sso_email_id=self.sso_email_id,
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )

        self.first_name = "John"
        self.last_name = "Doe"
        self.emails = [
            {
                "address": "email1@email.com",
                "type": str(EmailTypes.VERIFIED),
                "preferred": False,
            },
            {
                "address": "email2@email.com",
                "type": str(EmailTypes.CONTACT),
                "preferred": True,
            },
        ]

    @pytest.mark.django_db
    def test_create(self):
        staff_sso_services.create(
            sso_email_id=self.sso_email_id,
            first_name=self.first_name,
            last_name=self.last_name,
            emails=self.emails,
        )

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
        self.assertEqual(StaffSSOProfileEmail.objects.first().type, "verified")
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

    def test_get_by_user_id(self):
        staff_sso_profile = staff_sso_services.create(
            sso_email_id=self.sso_email_id,
            first_name=self.first_name,
            last_name=self.last_name,
            emails=self.emails,
        )
        actual = staff_sso_services.get_by_user_id(staff_sso_profile.user.pk)
        self.assertEqual(actual.user.sso_email_id, "email@email.com")
        self.assertEqual(actual.first_name, "John")
        self.assertEqual(actual.last_name, "Doe")

    @pytest.mark.django_db
    def test_update(self):
        staff_sso_profile = staff_sso_services.create(
            sso_email_id=self.sso_email_id,
            first_name=self.first_name,
            last_name=self.last_name,
            emails=self.emails,
        )
        kwargs = {
            "first_name": "newTom",
            "last_name": "newJones",
        }
        emails = [
            {
                "address": "email2@email.com",
                "type": EmailTypes.CONTACT,
                "preferred": False,
            }
        ]

        # check values before update
        staff_sso_email = StaffSSOProfileEmail.objects.filter(
            email=Email.objects.get(address="email2@email.com")
        )[0]
        self.assertTrue(staff_sso_email.preferred)
        self.assertEqual(staff_sso_profile.first_name, self.first_name)
        self.assertEqual(staff_sso_profile.last_name, self.last_name)

        staff_sso_services.update(id=staff_sso_profile.user.pk, emails=emails, **kwargs)
        staff_sso_profile.refresh_from_db()

        self.assertEqual(staff_sso_profile.first_name, "newTom")
        self.assertEqual(staff_sso_profile.last_name, "newJones")
        staff_sso_email = StaffSSOProfileEmail.objects.filter(
            email=Email.objects.get(address="email2@email.com")
        )[0]
        self.assertFalse(staff_sso_email.preferred)
