import pytest
from django.test import TestCase

from profiles import services
from profiles.models import EMAIL_TYPE_CONTACT, EMAIL_TYPE_WORK
from user.models import User


class ProfileServiceTest(TestCase):

    @pytest.mark.django_db
    def setUp(self): ...
