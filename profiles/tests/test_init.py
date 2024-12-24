import pytest
from django.test import TestCase


class ProfileServiceTest(TestCase):
    @pytest.mark.django_db
    def setUp(self): ...
