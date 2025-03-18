from django.db import connection, transaction
from django.db.models import QuerySet, Subquery

from profiles.models.peoplefinder import (
    PeopleFinderProfileTeam,
    PeopleFinderTeam,
    PeopleFinderTeamTree,
)


class TeamServiceError(Exception):
    pass


class TeamService:
    def add_team_to_teamtree(self, team: PeopleFinderTeam, parent: PeopleFinderTeam) -> None:
        """Add a team into the hierarchy.

        Args:
            team (Team): The team to be added.
            parent (Team): The parent team.
        """
        PeopleFinderTeamTree.objects.bulk_create(
            [
                # reference to itself
                PeopleFinderTeamTree(parent=team, child=team, depth=0),
                # all required tree connections
                *(
                    PeopleFinderTeamTree(
                        parent=tt.parent, child=team, depth=tt.depth + 1
                    )
                    for tt in PeopleFinderTeamTree.objects.filter(child=parent)
                ),
            ]
        )

    def validate_team_parent_update(
        self, team: PeopleFinderTeam, parent: PeopleFinderTeam
    ) -> None:
        """Validate that the new parent is valid for the given team.

        Args:
            team (Team):The team to be updated.
            parent (Team): The given parent team.

        Raises:
            TeamServiceError: If team's parent is not a valid parent.
        """
        if parent == team:
            raise TeamServiceError("A team's parent cannot be the team itself")

        if parent in self.get_all_child_teams(team):
            raise TeamServiceError("A team's parent cannot be a team's child")

        if parent and (team == self.get_root_team()):
            raise TeamServiceError("Cannot update the parent of the root team")

    @transaction.atomic
    def update_team_parent(
        self, team: PeopleFinderTeam, parent: PeopleFinderTeam
    ) -> None:
        """Update a team's parent with the given parent team.

        The implementation was informed by the following blog:
        https://www.percona.com/blog/2011/02/14/moving-subtrees-in-closure-table/

        Args:
            team (Team): The team to be updated.
            parent (Team): The given parent team.
        """
        self.validate_team_parent_update(team, parent)

        PeopleFinderTeamTree.objects.filter(
            child__in=Subquery(
                PeopleFinderTeamTree.objects.filter(parent=team).values("child")
            )
        ).exclude(
            parent__in=Subquery(
                PeopleFinderTeamTree.objects.filter(parent=team).values("child")
            )
        ).delete()

        with connection.cursor() as c:
            c.execute(
                """
                INSERT INTO peoplefinder_peoplefinderteamtree (parent_id, child_id, depth)
                SELECT
                    supertree.parent_id,
                    subtree.child_id,
                    (supertree.depth + subtree.depth + 1)
                FROM peoplefinder_peoplefinderteamtree AS supertree
                CROSS JOIN peoplefinder_peoplefinderteamtree AS subtree
                WHERE
                    subtree.parent_id = %s
                    AND supertree.child_id = %s
                """,
                [team.id, parent.id],
            )

    def get_all_child_teams(
        self, parent: PeopleFinderTeam
    ) -> QuerySet[PeopleFinderTeam]:
        """Return all child teams of the given parent team.

        Args:
            parent (Team): The given parent team.

        Returns:
            QuerySet: A queryset of teams.
        """
        return PeopleFinderTeam.objects.filter(children__parent=parent).exclude(
            children__child=parent
        )

    def get_root_team(self) -> PeopleFinderTeam:
        """Return the root team.

        Returns:
            Team: The root team.
        """
        teams_with_parents = PeopleFinderTeamTree.objects.filter(depth__gt=0)

        return PeopleFinderTeam.objects.exclude(
            id__in=Subquery(teams_with_parents.values("child"))
        ).get()

    def get_team_members(
        self, team: PeopleFinderTeam
    ) -> QuerySet[PeopleFinderProfileTeam]:
        sub_teams = self.get_all_child_teams(team)
