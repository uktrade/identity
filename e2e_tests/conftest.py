import json
from dataclasses import dataclass
from random import randrange

import pytest
from django.contrib.auth.models import AbstractUser
from django.test.client import Client
from factory.faker import faker


@dataclass
class State:
    client: Client
    user: AbstractUser


@pytest.fixture()
def state(db, basic_user):
    client = Client()
    client.force_login(basic_user)
    return State(client=client, user=basic_user)


@pytest.fixture
def scim_user_factory():
    def _factory(id=None):
        factory_faker = faker.Faker()

        if id is None:
            id = factory_faker.email()
        first_name = factory_faker.first_name()
        last_name = factory_faker.last_name()
        email = factory_faker.email()
        emails = []
        num_emails = randrange(1, stop=5)
        contact_email = randrange(1, stop=num_emails + 1)
        for i in range(num_emails):
            value = factory_faker.email()
            type = "work"
            primary = False

            if i == 1:
                value = email
                primary = True

            if contact_email == i + 1:
                type = "contact"

            emails.append({"value": value, "type": type, "primary": primary})

        return json.dumps(
            {
                "externalId": id,
                "id": id,
                "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
                "userName": email,
                "name": {
                    "familyName": last_name,
                    "givenName": first_name,
                },
                "displayName": f"{first_name} {last_name}",
                "active": True,
                "emails": emails,
            }
        )

    return _factory
