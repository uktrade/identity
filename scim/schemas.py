from dataclasses import dataclass

from ninja import Field, Schema

from user.models import User


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


# @dataclass
# class PhoneNumber:
#     value: str | None = None
#     type: str | None = None
#     primary: bool = False

# @dataclass
# class Address:
#     type: str | None = None
#     formatted: str | None = None
#     streetAddress: str | None = None
#     locality: str | None = None
#     region: str | None = None
#     postalCode: str | None = None
#     country: str | None = None


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
    # displayName: str | None = None
    # nickName: str | None = None
    # profileUrl: str | None = None
    # title: str | None = None
    # userType: str | None = None
    # preferredLanguage: str | None = None
    # locale: str | None = None
    # timezone: str | None = None
    active: bool | None = None
    emails: list[Email] | None = None
    # phoneNumbers: list[PhoneNumber] | None = None
    # ims: str | None = None
    # photos: str | None = None
    # addresses: list[Address] | None = None
    # groups
    # entitlements
    # roles
    # x509Certificates


class CreateUserRequest(ScimUserSchema): ...


class CreateUserResponse(ScimUserSchemaRequired):
    id = Field(alias="pk")
    externalId = Field(alias="sso_email_id")
    userName = Field(alias="sso_email_id")
    active = Field(alias="is_active")

    class Meta:
        model = User
        fields = []

    @staticmethod
    def resolve_name(obj: User):
        from profiles.services import combined

        combined_profile = combined.get_by_id(obj.sso_email_id)
        return Name(
            givenName=combined_profile.first_name,
            familyName=combined_profile.last_name,
        )

    @staticmethod
    def resolve_emails(obj: User):
        # TODO: We need a better way of getting ALL of a user's emails and
        # their type/primary status
        return [Email(value=obj.email, type="work", primary=True)]
