import pytest
from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.fixture(autouse=True)
def basic_user():
    return User.objects.create_user(
        sso_email_id="sso_email_id@email.com",
        is_active=True,
        is_staff=False,
        is_superuser=False,
    )
