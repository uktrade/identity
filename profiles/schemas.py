from dataclasses import dataclass
from typing import Any, Dict, List

from django.contrib.auth import get_user_model
from ninja import Field, ModelSchema, Schema

from profiles.models.generic import Profile


@dataclass
class Name:
    givenName: str | None = None
    familyName: str | None = None
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


class ProfileMinimal(ModelSchema):
    id: str = Field(alias="sso_email_id")

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "preferred_email",
        ]
