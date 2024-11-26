from dataclasses import dataclass
from typing import List

from django.contrib.auth import get_user_model
from ninja import Field, Schema


user = get_user_model()


@dataclass
class Name:
    givenName: str
    familyName: str
    formatted: str = None
    middleName: str = None
    honorificPrefix: str = None
    honorificSuffix: str = None

    def __init__(self, first_name, last_name):
        self.givenName = first_name
        self.familyName = last_name


@dataclass
class Email:
    value: str = None
    type: str = None
    primary: bool = False

    def __init__(self, value, type, primary):
        self.value = value
        self.type = type
        self.primary = primary


class SCIMUser(Schema):
    class Config:
        populate_by_name = True

    schemas: List = ["urn:ietf:params:scim:schemas:core:2.0:User"]
    userName: str = Field(alias="username")
    name: Name
    displayName: str = None
    nickName: str = None
    profileUrl: str = None
    title: str = None
    userType: str = None
    preferredLanguage: str = None
    locale: str = None
    timezone: str = None
    active: bool = Field(alias="is_active")
    emails: list[Email] = None
    ims: str = None
    photos: str = None

    @staticmethod
    def resolve_emails(obj):
        if type(obj) is get_user_model():
            if obj.email:
                return [Email(obj.email, "work", True)]
        else:
            if "emails" in obj:
                return obj["emails"]
            else:
                return None

    @staticmethod
    def resolve_name(obj):
        if type(obj) is get_user_model():
            return Name(obj.first_name, obj.last_name)
        else:
            return obj["name"]
