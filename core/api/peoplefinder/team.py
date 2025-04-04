from ninja import Router

from core import services as core_services
from core.schemas import Error
from core.schemas.peoplefinder.team import (
    CreateTeamRequest,
    PeopleFinderTeamHierarchyResponse,
    PeopleFinderTeamMinimalResponse,
    PeopleFinderTeamResponse,
    PeopleFinderTeamUpdateResponse,
    UpdateTeamRequest,
)
from profiles.exceptions import ParentTeamDoesNotExist, TeamExists, TeamParentError
from profiles.models.peoplefinder import PeopleFinderTeam, PeopleFinderTeamData
from profiles.types import UNSET


router = Router()
team_router = Router()
router.add_router("teams", team_router)


@team_router.get(
    "",
    response={
        200: PeopleFinderTeamHierarchyResponse,
        500: Error,
    },
)
def get_hierarcy_of_all_teams(request) -> tuple[int, PeopleFinderTeamData | dict]:
    """Endpoint to return the full peoplefinder team hierarcy"""
    try:
        return 200, core_services.get_peoplefinder_team_hierarchy()
    except Exception as unknown_error:
        return 500, {
            "message": f"Could not get the team hierarchy, reason: {unknown_error}"
        }


@team_router.get(
    "{slug}",
    response={
        200: PeopleFinderTeamResponse,
        404: Error,
    },
)
def get_team(request, slug: str) -> tuple[int, PeopleFinderTeamData | dict]:
    """Endpoint to return a peoplefinder team record and parent team(s) information"""
    try:
        team = core_services.get_peoplefinder_team_by_slug(slug=slug)
        return 200, core_services.get_peoplefinder_team_and_parents(team)
    except PeopleFinderTeam.DoesNotExist:
        return 404, {"message": "People finder team does not exist"}


@team_router.post(
    "",
    response={
        201: PeopleFinderTeamMinimalResponse,
        404: Error,
    },
)
def create_team(request, team_request: CreateTeamRequest) -> tuple[int, dict]:
    """Endpoint to create a new people finder team"""
    try:
        parent = core_services.get_peoplefinder_team_by_slug(team_request.parent_slug)
    except PeopleFinderTeam.DoesNotExist:
        return 404, {
            "message": "Cannot create the people finder team, parent team does not exist"
        }
    try:
        return 201, core_services.create_peoplefinder_team(
            slug=team_request.slug,
            name=team_request.name,
            abbreviation=team_request.abbreviation,
            description=team_request.description,
            leaders_ordering=team_request.leaders_ordering,
            cost_code=team_request.cost_code,
            team_type=team_request.team_type,
            parent=parent,
        )
    except (ParentTeamDoesNotExist, TeamExists, TeamParentError) as e:
        return 404, {"message": str(e)}


@team_router.put(
    "{slug}",
    response={
        200: PeopleFinderTeamUpdateResponse,
        404: Error,
    },
)
def update_team(
    request, slug: str, team_request: UpdateTeamRequest
) -> tuple[int, PeopleFinderTeamData | dict]:
    """Endpoint to update an existing people finder team"""
    parent = None
    if team_request.parent_slug:
        try:
            parent = core_services.get_peoplefinder_team_by_slug(
                team_request.parent_slug
            )
        except PeopleFinderTeam.DoesNotExist:
            return 404, {
                "message": "Cannot update the people finder team, parent team does not exist"
            }
    try:
        team = core_services.get_peoplefinder_team_by_slug(slug=slug)
        core_services.update_peoplefinder_team(
            slug=slug,
            name=team_request.name,
            abbreviation=(
                UNSET
                if team_request.abbreviation is None
                else team_request.abbreviation
            ),
            description=(
                UNSET if team_request.description is None else team_request.description
            ),
            leaders_ordering=(
                UNSET
                if team_request.leaders_ordering is None
                else team_request.leaders_ordering
            ),
            cost_code=(
                UNSET if team_request.cost_code is None else team_request.cost_code
            ),
            team_type=(
                UNSET if team_request.team_type is None else team_request.team_type
            ),
            parent=parent,
        )
        team.refresh_from_db()
        return 200, core_services.get_peoplefinder_team_and_parents(team=team)
    except TeamParentError as e:
        return 404, {"message": str(e)}
    except PeopleFinderTeam.DoesNotExist:
        return 404, {"message": "People finder team does not exist"}
