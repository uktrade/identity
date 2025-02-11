import pytest
from django.contrib.auth import get_user_model

from profiles.models.combined import Profile
from profiles.models.generic import Email
from profiles.models.staff_sso import StaffSSOProfile, StaffSSOProfileEmail


pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture(autouse=True, scope="function")
def basic_user():
    return User.objects.create_user(
        sso_email_id="sso_email_id@email.com",
        is_active=True,
        is_staff=False,
        is_superuser=False,
    )


@pytest.fixture(scope="function")
def sso_profile(basic_user):
    email1 = Email.objects.create(address="email1@email.com")
    email2 = Email.objects.create(address="email2@email.com")
    sso_profile = StaffSSOProfile.objects.create(
        user=basic_user,
        first_name="John",
        last_name="Doe",
    )
    StaffSSOProfileEmail.objects.create(
        profile=sso_profile,
        email=email1,
        is_primary=False,
    )
    StaffSSOProfileEmail.objects.create(
        profile=sso_profile,
        email=email2,
        is_primary=True,
    )
    return sso_profile


@pytest.fixture(scope="function")
def combined_profile(sso_profile):
    return Profile.objects.create(
        sso_email_id=sso_profile.user.pk,
        first_name="John",
        last_name="Doe",
        primary_email="email2@email.com",
        emails=[
            "email1@email.com",
            "email2@email.com",
        ],
        is_active=True,
    )
