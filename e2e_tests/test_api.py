import json

import pytest
from django.test.client import Client
from django.urls import reverse

from core import services
from profiles.models.combined import Profile


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.e2e,
    pytest.mark.xfail,  #  @TODO implement when routes and test/auth sorted
]


def test_unauthenticated_request(scim_user_factory):
    assert False


def test_authenticated_request(scim_user_factory):
    assert False


def test_unauthenticated_docs_request(scim_user_factory):
    assert False


def test_authenticated_docs_request(scim_user_factory):
    assert False
