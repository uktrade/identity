import pytest
from django.test import TestCase

from profiles.models import EMAIL_TYPE_WORK, EMAIL_TYPE_CONTACT
from profiles import services
from user.models import User


class ProfileServiceTest(TestCase):

    @pytest.mark.django_db
    def setUp(self):
        ...
