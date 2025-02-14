import pytest
from django.test import override_settings


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.e2e,
]


def test_files_processed_to_python():
    assert False


def test_files_processed_to_django_model_instances():
    assert False
