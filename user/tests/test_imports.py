import pytest

from user.utils import StaffSSOUserS3Ingest


pytestmark = pytest.mark.django_db


@pytest.mark.e2e
def test_new_users_are_added():
    assert False


@pytest.mark.e2e
def test_changed_users_are_updated():
    assert False


@pytest.mark.e2e
def test_missing_users_are_deleted():
    assert False


def test_mapping():
    assert False


def test_postprocess_all():
    assert False


def test_postprocess_object():
    assert False
