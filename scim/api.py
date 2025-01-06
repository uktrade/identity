from ninja import Router

from core import services as core_services
from profiles import services as profile_services
from profiles.models.combined import Profile
from scim.schemas import (
    CreateUserRequest,
    CreateUserResponse,
    GetUserResponse,
    UpdateUserRequest,
    UpdateUserResponse,
)
from scim.schemas.scim import ScimErrorSchema
from user.exceptions import UserExists
from user.models import User


router = Router()


@router.get(
    "scim/v2/Users/{id}",
    response={
        200: GetUserResponse,
        404: ScimErrorSchema,
    },
)
def get_user(request, id: str):
    """In fact returns the combined Profile"""
    try:
        return profile_services.get_by_id(id)
    except Profile.DoesNotExist:
        return 404, {
            "status": "404",
            "detail": "Unable to find user",
        }


@router.post("scim/v2/Users", response={201: CreateUserResponse, 409: ScimErrorSchema})
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
    "scim/v2/Users/{id}",
    response={200: UpdateUserResponse, 201: CreateUserResponse, 400: ScimErrorSchema},
)
def update_user(
    request, id: str, scim_user: UpdateUserRequest
) -> tuple[int, Profile | dict]:

    all_emails = [email.value for email in scim_user.emails]
    try:
        profile = core_services.update_identity(
            id=id,
            first_name=scim_user.name.givenName,
            last_name=scim_user.name.familyName,
            all_emails=all_emails,
            primary_email=scim_user.get_primary_email(),
            contact_email=scim_user.get_contact_email(),
        )
        return 200, profile
    except User.DoesNotExist:
        profile = core_services.create_identity(
            id=id,
            first_name=scim_user.name.givenName,
            last_name=scim_user.name.familyName,
            all_emails=all_emails,
            primary_email=scim_user.get_primary_email(),
            contact_email=scim_user.get_contact_email(),
        )
        return 201, profile
    except ValueError as e:
        return 400, {
            "status": "400",
            "detail": e.args[0],
        }
