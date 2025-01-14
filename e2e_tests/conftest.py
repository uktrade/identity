from dataclasses import dataclass

import pytest
from django.contrib.auth.models import AbstractUser
from django.test.client import Client


@dataclass
class State:
    client: Client
    user: AbstractUser


@pytest.fixture()
def state(db, basic_user):
    client = Client()
    client.force_login(basic_user)
    return State(client=client, user=basic_user)
