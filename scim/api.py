from ninja import Router

from core import services as core_services
from core.schemas import Error
from profiles import services as profile_services
from profiles.models.combined import Profile
from scim.schemas import CreateUserRequest, CreateUserResponse, GetUserResponse
from user.exceptions import UserExists
from user.models import User


router = Router()


@router.get(
    "scim/v2/Users/{id}",
    response={
        200: GetUserResponse,
        404: Error,
    },
)
def get_user(request, id: str):
    """In fact returns the combined Profile"""
    try:
        return profile_services.get_by_id(id)
    except Profile.DoesNotExist:
        return 404, {"message": "No user found with that ID"}


@router.post("scim/v2/Users", response={201: CreateUserResponse, 409: Error})
def create_user(request, scim_user: CreateUserRequest) -> tuple[int, User | dict]:
    if not scim_user.active:
        # TODO: Discuss what should happen in this scenario
        raise Exception("WHY ARE WE BEING INFORMED OF A NEW USER THAT IS INACTIVE?")

    emails: list[dict] = []
    if scim_user.emails:
        # TODO: BUILD EMAIL DICTS
        emails = [
            {
                "address": e.value,
            }
            for e in scim_user.emails
        ]

    assert scim_user.name
    assert scim_user.name.givenName
    assert scim_user.name.familyName

    try:
        user = core_services.create_identity(
            id=scim_user.externalId,
            first_name=scim_user.name.givenName,
            last_name=scim_user.name.familyName,
            emails=emails,
        )
        return 201, user
    except UserExists:
        return 409, {"message": "A user with that ID already exists"}
