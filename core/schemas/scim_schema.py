from dataclasses import dataclass
from typing import Dict, List

from django.contrib.auth import get_user_model
from ninja import Field, Schema


user = get_user_model()


@dataclass
class Name:
    givenName: str
    familyName: str
    formatted: str | None = None
    middleName: str | None = None
    honorificPrefix: str | None = None
    honorificSuffix: str | None = None


@dataclass
class Email:
    value: str | None = None
    type: str | None = None
    primary: bool = False


class SCIMUser(Schema):
    class Config:
        populate_by_name = True

    schemas: List = ["urn:ietf:params:scim:schemas:core:2.0:User"]
    userName: str = Field(alias="username")
    name: Name
    displayName: str | None = None
    nickName: str | None = None
    profileUrl: str | None = None
    title: str | None = None
    userType: str | None = None
    preferredLanguage: str = None
    locale: str | None = None
    timezone: str | None = None
    active: bool = Field(alias="is_active")
    emails: list[Email] | None = None
    ims: str | None = None
    photos: str | None = None

    @staticmethod
    def resolve_emails(obj: Dict[any, any] | get_user_model):
        if type(obj) is get_user_model():
            if obj.email:
                return [Email(obj.email, "work", True)]
        else:
            if "emails" in obj:
                return obj["emails"]
            else:
                return None

    @staticmethod
    def resolve_name(obj: Dict[any, any] | get_user_model):
        if type(obj) is get_user_model():
            return Name(obj.first_name, obj.last_name)
        else:
            return obj["name"]
