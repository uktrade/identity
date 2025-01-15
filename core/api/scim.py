from ninja import Router

from core import services as core_services
from core.schemas.scim import (
    CreateUserRequest,
    CreateUserResponse,
    GetUserResponse,
    ScimErrorSchema,
    UpdateUserRequest,
    UpdateUserResponse,
)
from profiles.models.combined import Profile
from user.exceptions import UserExists
from user.models import User


router = Router()


@router.get(
    "/{id}",
    response={
        200: GetUserResponse,
        404: ScimErrorSchema,
    },
)
def get_user(request, id: str):
    """In fact returns the combined Profile"""
    try:
        return core_services.get_by_id(id)
    except Profile.DoesNotExist:
        return 404, {
            "status": "404",
            "detail": "Unable to find user",
        }


@router.post("", response={201: CreateUserResponse, 409: ScimErrorSchema})
def create_user(request, scim_user: CreateUserRequest) -> tuple[int, User | dict]:
    if not scim_user.active:
        raise ValueError("Cannot create inactive profile via SCIM")

    if not scim_user.emails:
        raise ValueError("Cannot create profile with no email")

    emails = [email.value for email in scim_user.emails]

    try:
        user = core_services.create_identity(
            id=scim_user.externalId,
            first_name=scim_user.name.givenName,
            last_name=scim_user.name.familyName,
            all_emails=emails,
            primary_email=scim_user.get_primary_email(),
            contact_email=scim_user.get_contact_email(),
        )
        return 201, user
    except UserExists as e:
        return 409, {
            "status": "409",
            "detail": e.message,
        }


@router.put(
    "/{id}",
    response={200: UpdateUserResponse, 404: ScimErrorSchema, 400: ScimErrorSchema},
)
def update_user(
    request, id: str, scim_user: UpdateUserRequest
) -> tuple[int, Profile | dict]:

    all_emails = [email.value for email in scim_user.emails]
    primary_email = scim_user.get_primary_email()
    contact_email = scim_user.get_contact_email()
    profile = core_services.get_by_id(id=id)
    try:
        core_services.update_identity(
            profile=profile,
            first_name=scim_user.name.givenName,
            last_name=scim_user.name.familyName,
            all_emails=all_emails,
            primary_email=str(primary_email) if primary_email else core_services.UNSET,
            contact_email=str(contact_email) if contact_email else core_services.UNSET,
            is_active=scim_user.active,
        )
        return 200, profile
    except User.DoesNotExist:
        return 404, {
            "status": "404",
            "detail": "User does not exist",
        }
    except ValueError as e:
        return 400, {
            "status": "400",
            "detail": e.args[0],
        }


@router.delete("/{id}", response={204: None, 404: ScimErrorSchema})
def delete_user(
    request,
    id: str,
) -> int | tuple[int, dict]:
    profile = core_services.get_by_id(id=id)
    try:
        core_services.delete_identity(
            profile=profile,
        )
        return 204
    except User.DoesNotExist:
        return 404, {
            "status": "404",
            "detail": "User does not exist",
        }
