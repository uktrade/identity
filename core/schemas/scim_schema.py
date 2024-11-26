from dataclasses import dataclass
from typing import Any, List

from django.contrib.auth import get_user_model
from ninja import Field, Schema
from pydantic import AliasChoices, ConfigDict, create_model


user = get_user_model()


class Name(Schema):
    model_config = ConfigDict(from_attributes=True)
    givenName: str
    familyName: str

    def __init__(self, first_name, last_name):
        self.givenName = first_name
        self.familyName = last_name


class SCIMRequest(Schema):
    schemas: List = ["urn:ietf:params:scim:schemas:core:2.0:User"]
    userName: str = Field(alias="username")
    name: Name = {
        "givenName": Field(alias="first_name"),
        "familyName": Field(alias="last_name"),
    }
    emails: str = Field(alias="email")
    active: bool = Field(alias="is_active")

    # name: Name = create_model('SCIMRequest', type=(str, ...), attributes=(Name(givenName=Field(alias="first_name"), familyName=Field(alias="last_name")), ...))
