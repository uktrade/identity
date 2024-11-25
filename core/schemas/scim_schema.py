from typing import List

from django.contrib.auth import get_user_model
from ninja import Field, Schema


user = get_user_model()


class Name(Schema):
    givenName: str  = Field(alias="first_name")
    familyName: str  = Field(alias="last_name")


class SCIMRequest(Schema):
    schemas: List = ["urn:ietf:params:scim:schemas:core:2.0:User"]
    userName: str = Field(alias="username")
    name: Name = None #resolvers?
    emails: str = Field(alias="email")
    active: bool = Field(alias="is_active")
