from django.db import connection, transaction
from django.db.models import QuerySet, Subquery

from profiles.exceptions import TeamServiceError
from profiles.models.peoplefinder import PeopleFinderTeam, PeopleFinderTeamTree


class TeamService:
    def add_team_to_teamtree(
        self, team: PeopleFinderTeam, parent: PeopleFinderTeam
    ) -> None:
        """Add a team into the hierarchy.

        Args:
            team (PeopleFinderTeam): The team to be added.
            parent (PeopleFinderTeam): The parent team.
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
            team (PeopleFinderTeam):The team to be updated.
            parent (PeopleFinderTeam): The given parent team.

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
            team (PeopleFinderTeam): The team to be updated.
            parent (PeopleFinderTeam): The given parent team.
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
                INSERT INTO profiles_peoplefinderteamtree (parent_id, child_id, depth)
                SELECT
                    supertree.parent_id,
                    subtree.child_id,
                    (supertree.depth + subtree.depth + 1)
                FROM profiles_peoplefinderteamtree AS supertree
                CROSS JOIN profiles_peoplefinderteamtree AS subtree
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
            parent (PeopleFinderTeam): The given parent team.

        Returns:
            QuerySet: A queryset of peoplefinder teams.
        """
        return PeopleFinderTeam.objects.filter(children__parent=parent).exclude(
            children__child=parent
        )

    def get_immediate_child_teams(
        self, parent: PeopleFinderTeam
    ) -> QuerySet[PeopleFinderTeam]:
        """Return all immediate child teams of the given parent team.

        Args:
            parent (PeopleFinderTeam): The given parent team.

        Returns:
            QuerySet: A queryset of peoplefinder teams.
        """
        return PeopleFinderTeam.objects.filter(
            children__parent=parent, children__depth=1
        )

    def get_root_team(self) -> PeopleFinderTeam:
        """Return the root team.

        Returns:
            PeopleFinderTeam: The root team.
        """
        teams_with_parents = PeopleFinderTeamTree.objects.filter(depth__gt=0)

        return PeopleFinderTeam.objects.exclude(
            id__in=Subquery(teams_with_parents.values("child"))
        ).get()

    def can_team_be_deleted(self, team: PeopleFinderTeam) -> tuple[bool, list[str]]:
        """Check and return whether a team can be deleted.

        Args:
            team (PeopleFinderTeam): The team to be deleted.

        Returns:
            tuple[bool, list[str]]: Whether the team can be deleted and the reasons why.
        """
        reasons = []

        sub_teams = self.get_all_child_teams(team)
        if sub_teams:
            reasons.append("sub-teams")

        has_members = self.get_team_members(team).exists()
        if has_members:
            reasons.append("members")

        if reasons:
            return False, reasons

        return True, []

    def get_team_members(self, team: PeopleFinderTeam):
        # TODO: We don't have active field in PeopleFinderProfileTeam model
        # In current people finder we use active to check if there are members
        # in a team.
        return NotImplementedError
