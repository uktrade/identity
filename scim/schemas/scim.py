# Comments are used for many fields in the schemas in this file.
# That's because these schemas specifically refer to the SCIM protocol,
# and the commented-out fields are specified in the protocol (and in
# the order they're in) but not represented in our data models.

from dataclasses import dataclass
from typing import Literal

from ninja import Schema


@dataclass
class Name:
    givenName: str
    familyName: str
    # formatted: str | None = None
    # middleName: str | None = None
    # honorificPrefix: str | None = None
    # honorificSuffix: str | None = None


@dataclass
class Email:
    value: str
    type: str | None = None
    primary: bool = False


class ScimCoreSchema(Schema):
    # See https://datatracker.ietf.org/doc/html/rfc7643#section-3.1
    id: str
    externalId: str
    # "meta" and some of its sub-attributes are required as part of the core SCIM schema
    # we will need to
    # meta


class ScimUserSchemaRequired(ScimCoreSchema):
    """
    Only the required values for a user object

    See: https://datatracker.ietf.org/doc/html/rfc7643#section-4.1
    """

    schemas: list[str] = ["urn:ietf:params:scim:schemas:core:2.0:User"]
    userName: str


class ScimUserSchema(ScimUserSchemaRequired):
    """
    All possible values for the user object

    Note: commented out values are not currently in use by this application.
    See: https://datatracker.ietf.org/doc/html/rfc7643#section-4.1
    """

    name: Name | None = None
    # displayName
    # nickName
    # profileUrl
    # title
    # userType
    # preferredLanguage
    # locale
    # timezone
    active: bool | None = None
    emails: list[Email] | None = None
    # phoneNumbers
    # ims
    # photos
    # addresses
    # groups
    # entitlements
    # roles
    # x509Certificates


class ScimErrorSchema(Schema):
    schemas: list[str] = ["urn:ietf:params:scim:api:messages:2.0:Error"]
    status: str
    detail: str | None = None
    scimType: (
        Literal[
            "invalidFilter",
            "tooMany",
            "uniqueness",
            "mutability",
            "invalidSyntax",
            "invalidPath",
            "noTarget",
            "invalidValue",
            "invalidVers",
            "sensitive",
        ]
        | None
    ) = None
