from ninja import Router

from core import services as core_services
from core.schemas import Error
from core.schemas.peoplefinder.team import PeopleFinderTeamSchema


router = Router()
team_router = Router()
router.add_router("team", team_router)


@team_router.get(
    "all",
    response={
        200: PeopleFinderTeamSchema,
        500: Error,
    },
)
def get_hierarcy_of_all_teams(request):
    try:
        return 200, core_services.get_peoplefinder_team_hierarchy()
    except Exception as unknown_error:
        return 500, {
            "message": f"Could not get the team hierarchy, reason: {unknown_error}"
        }
