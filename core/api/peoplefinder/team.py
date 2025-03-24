from ninja import Router

from core import services as core_services
from core.schemas.peoplefinder.team import PeopleFinderTeamTreeResponse


router = Router()
team_router = Router()
router.add_router("team", team_router)


@team_router.get(
    "all",
    response={
        200: list[PeopleFinderTeamTreeResponse],
    },
)
def get_all_teams(request):
    return 200, core_services.get_peoplefinder_team_hierarchy()
