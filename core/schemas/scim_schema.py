from dataclasses import dataclass
from typing import Any, Dict, List

from django.contrib.auth import get_user_model
from ninja import Field, Schema


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


@dataclass
class PhoneNumber:
    value: str | None = None
    type: str | None = None
    primary: bool = False


@dataclass
class Address:
    type: str | None = None
    formatted: str | None = None
    streetAddress: str | None = None
    locality: str | None = None
    region: str | None = None
    postalCode: str | None = None
    country: str | None = None


class SCIMUser(Schema):
    schemas: List = ["urn:ietf:params:scim:schemas:core:2.0:User"]
    id: Any | None = None
    externalId: Any | None = None
    userName: str = Field(alias="username")
    name: Name
    displayName: str | None = None
    nickName: str | None = None
    profileUrl: str | None = None
    title: str | None = None
    userType: str | None = None
    preferredLanguage: str | None = None
    locale: str | None = None
    timezone: str | None = None
    active: bool = Field(alias="is_active")
    emails: list[Email] | None = None
    phoneNumbers: list[PhoneNumber] | None = None
    ims: str | None = None
    photos: str | None = None
    addresses: list[Address] | None = None

    @staticmethod
    def resolve_emails(obj: Dict[Any, Any] | get_user_model):
        if type(obj) is get_user_model():
            if obj.email:
                return [Email(obj.email, "work", True)]
        else:
            if "emails" in obj:
                return obj["emails"]
            else:
                return None

    @staticmethod
    def resolve_name(obj: Dict[Any, Any] | get_user_model):
        if type(obj) is get_user_model():
            return Name(obj.first_name, obj.last_name)
        else:
            return obj["name"]

    @staticmethod
    def resolve_phoneNumbers(obj: Dict[Any, Any] | get_user_model):
        if type(obj) is get_user_model():
            return [PhoneNumber("0123456789", "work", True)]
        else:
            if "phoneNumbers" in obj:
                return obj["phoneNumbers"]
            else:
                return None

    @staticmethod
    def resolve_addresses(obj: Dict[Any, Any] | get_user_model):
        if type(obj) is get_user_model():
            return [Address("work")]
        else:
            if "addresses" in obj:
                return obj["addresses"]
            else:
                return None
