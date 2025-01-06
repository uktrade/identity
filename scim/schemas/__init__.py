from ninja import Field

from profiles.models.combined import Profile
from scim.schemas.scim import Email, Name, ScimUserSchema, ScimUserSchemaRequired
from user.models import User


class MinimalUserRequest(ScimUserSchema):
    """
    Our application's expectation of the minimum fields required when receiving
    user data.
    """

    name: Name
    emails: list[Email]

    def get_primary_email(self) -> str | None:
        primary_email = None
        if self.emails:
            for email in self.emails:
                if email.primary:
                    primary_email = str(email)
        return primary_email

    def get_contact_email(self) -> str | None:
        if self.emails:
            for email in self.emails:
                if email.type == "contact":
                    return str(email)
        return None


class MinimalUserResponse(ScimUserSchemaRequired):
    """
    Our application's expectation of the minimum fields required when returning
    user data.

    Note: populated by a combined Profile
    """

    id: str = Field(alias="pk")
    externalId: str = Field(alias="sso_email_id")
    userName: str = Field(alias="sso_email_id")
    active: bool = Field(alias="is_active")

    @staticmethod
    def resolve_name(obj: Profile):
        # @TODO we should be using preferred name once it's available
        return Name(
            givenName=obj.first_name,
            familyName=obj.last_name,
        )

    @staticmethod
    def resolve_emails(obj: User):
        # TODO: We need a better way of getting ALL of a user's emails and
        # their type/primary status
        return [Email(value=obj.email, type="verified", primary=True)]


class CreateUserRequest(MinimalUserRequest): ...


class CreateUserResponse(MinimalUserResponse): ...


class UpdateUserRequest(MinimalUserRequest): ...


class UpdateUserResponse(MinimalUserResponse): ...


class GetUserResponse(MinimalUserResponse): ...
