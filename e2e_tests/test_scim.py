import pytest
from factory.faker import faker


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.e2e,
]
