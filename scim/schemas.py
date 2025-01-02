# Comments are used for many fields in the schemas in this file.
# That's because these schemas specifically refer to the SCIM protocol,
# and the commented-out fields are specified in the protocol (and in
# the order they're in) but not represented in our data models.

from dataclasses import dataclass

from ninja import Field, Schema

from profiles.models.combined import Profile
from user.models import User


@dataclass
class Name:
    givenName: str | None = None
    familyName: str | None = None
    # formatted: str | None = None
    # middleName: str | None = None
    # honorificPrefix: str | None = None
    # honorificSuffix: str | None = None


@dataclass
class Email:
    value: str | None = None
    type: str | None = None
    primary: bool = False


class ScimCoreSchema(Schema):
    # See https://datatracker.ietf.org/doc/html/rfc7643#section-3.1
    id: str
    externalId: str
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


class MinimalUserResponse(ScimUserSchemaRequired):
    """Designed to be populated by a combined Profile"""

    id: str = Field(alias="pk")
    externalId: str = Field(alias="sso_email_id")
    userName: str = Field(alias="sso_email_id")
    active: bool = Field(alias="is_active")

    @staticmethod
    def resolve_name(obj: Profile):
        # @TODO should we be using preferred name?
        return Name(
            givenName=obj.first_name,
            familyName=obj.last_name,
        )

    @staticmethod
    def resolve_emails(obj: User):
        # TODO: We need a better way of getting ALL of a user's emails and
        # their type/primary status
        return [Email(value=obj.email, type="verified", primary=True)]


class CreateUserRequest(ScimUserSchema):
    def get_primary_email(self) -> str | None:
        primary_email = None
        if self.emails:
            for email in self.emails:
                if email.primary:
                    primary_email = str(email)
        return primary_email


class CreateUserResponse(MinimalUserResponse): ...


class GetUserResponse(MinimalUserResponse): ...


class PutUserResponse(MinimalUserResponse): ...
