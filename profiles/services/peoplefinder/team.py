from typing import Optional

from django.db import connection, transaction
from django.db.models import Q, QuerySet, Subquery

from profiles.exceptions import (
    ParentTeamDoesNotExist,
    TeamChildError,
    TeamExists,
    TeamMemberError,
    TeamParentError,
    TeamRootError,
)
from profiles.models.peoplefinder import (
    PeopleFinderProfileTeam,
    PeopleFinderTeam,
    PeopleFinderTeamData,
    PeopleFinderTeamLeadersOrdering,
    PeopleFinderTeamTree,
    PeopleFinderTeamType,
)
from profiles.types import UNSET, Unset


def get_by_slug(slug: str) -> PeopleFinderTeam:
    """
    Retrieve a People Finder Team by its Slug.
    """
    return PeopleFinderTeam.objects.get(slug=slug)


def create(
    slug: str,
    name: str,
    abbreviation: Optional[str],
    description: Optional[str],
    leaders_ordering: Optional[PeopleFinderTeamLeadersOrdering],
    cost_code: Optional[str],
    team_type: Optional[PeopleFinderTeamType],
    parent: PeopleFinderTeam,
) -> PeopleFinderTeam:
    """
    Creates a people finder team
    """
    try:
        PeopleFinderTeam.objects.get(slug=slug)
        raise TeamExists("Team has been previously created")
    except PeopleFinderTeam.DoesNotExist:
        team = PeopleFinderTeam(
            slug=slug,
            name=name,
            abbreviation=abbreviation,
            description=description,
            leaders_ordering=leaders_ordering,
            cost_code=cost_code,
            team_type=team_type,
        )
    # Validate team parent
    if parent not in PeopleFinderTeam.objects.all():
        raise ParentTeamDoesNotExist(
            "Cannot create the people finder team, parent team does not exist"
        )

    if not PeopleFinderTeamTree.objects.filter(parent__id=parent.id).exists():
        raise TeamParentError("Parent team is not in the team hierarchy")

    # Validate and save the new team to db
    team.full_clean()
    team.save()

    # Add team to the team tree
    add_team_to_teamtree(team=team, parent=parent)

    return team


def update(
    peoplefinder_team: PeopleFinderTeam,
    name: Optional[str | Unset] = None,
    abbreviation: Optional[str | Unset] = None,
    description: Optional[str | Unset] = None,
    leaders_ordering: Optional[str | PeopleFinderTeamLeadersOrdering | Unset] = None,
    cost_code: Optional[str | Unset] = None,
    team_type: Optional[str | PeopleFinderTeamType | Unset] = None,
    parent: Optional[PeopleFinderTeam] = None,
) -> None:

    update_fields: list = []

    if name is not None:
        if name is UNSET:
            peoplefinder_team.name = None
        else:
            peoplefinder_team.name = name
        update_fields.append("name")
    if abbreviation is not None:
        if abbreviation is UNSET:
            peoplefinder_team.abbreviation = None
        else:
            peoplefinder_team.abbreviation = abbreviation
        update_fields.append("abbreviation")
    if description is not None:
        if description is UNSET:
            peoplefinder_team.description = None
        else:
            peoplefinder_team.description = description
        update_fields.append("description")
    if leaders_ordering is not None:
        if leaders_ordering is UNSET:
            peoplefinder_team.leaders_ordering = None
        else:
            peoplefinder_team.leaders_ordering = leaders_ordering
        update_fields.append("leaders_ordering")
    if cost_code is not None:
        if cost_code is UNSET:
            peoplefinder_team.cost_code = None
        else:
            peoplefinder_team.cost_code = cost_code
        update_fields.append("cost_code")
    if team_type is not None:
        if team_type is UNSET:
            peoplefinder_team.team_type = None
        else:
            peoplefinder_team.team_type = team_type
        update_fields.append("team_type")

    peoplefinder_team.full_clean()
    peoplefinder_team.save(update_fields=update_fields)

    # Update team parent
    if parent:
        update_team_parent(team=peoplefinder_team, parent=parent)


def delete(team: PeopleFinderTeam) -> None:
    """
    Deletes a team and removes it from the team tree.
    """
    parent = get_immediate_parent_team(child=team)
    team_tree = get_all_child_teams(parent=team)
    members = get_team_members(team=team)

    if team_tree:
        raise TeamChildError("Cannot delete a team that contains children")

    if members:
        raise TeamMemberError("Cannot delete a team that contains active members")

    if parent is None and (team == get_root_team()):
        raise TeamRootError("Cannot delete the root team")

    remove_team_parent(team=team)
    # Hard delete team object
    team.delete()


def get_team_hierarchy() -> PeopleFinderTeamData:
    """
    Get all teams data in the team tree
    """
    root_team = get_root_team()
    children_depth_1 = PeopleFinderTeamTree.objects.select_related(
        "child", "parent"
    ).filter(depth=1)
    children_map: dict = {}

    for relation in children_depth_1:
        if relation.parent_id not in children_map:
            children_map[relation.parent_id] = []
        children_map[relation.parent_id].append(relation.child)

    def build_team_node(team):
        return {
            "slug": team.slug,
            "name": team.name,
            "abbreviation": team.abbreviation,
            "children": [
                build_team_node(child) for child in children_map.get(team.id, [])
            ],
        }

    return build_team_node(root_team)


def get_team_and_parents(team: PeopleFinderTeam) -> PeopleFinderTeamData:
    """
    Get a team and its parents data
    """
    parents_team_tree = (
        PeopleFinderTeamTree.objects.select_related("child", "parent")
        .filter(child=team)
        .exclude(parent=team)
        .order_by("depth")
    )
    return {
        "slug": team.slug,
        "name": team.name,
        "abbreviation": team.abbreviation,
        "children": None,
        "parents": [
            {
                "slug": branch.parent.slug,
                "name": branch.parent.name,
                "abbreviation": branch.parent.abbreviation,
                "depth": branch.depth,
            }
            for branch in parents_team_tree
        ],
    }


def add_team_to_teamtree(team: PeopleFinderTeam, parent: PeopleFinderTeam) -> None:
    """Add a team into the hierarchy.

    Args:
        team (PeopleFinderTeam): The team to be added.
        parent (PeopleFinderTeam): The parent team.

    Details of implementation:

    The PeopleFinderTeamTree is a closure table where
    we have PeopleFinderTeam objects as nodes and we use
    the PeopleFinderTeamTree to store information about
    the tree/hierarchy structure.

    Example: We have a team tree of A -> B and want to add a new node C to the hierarchy

    Current hierarchy:
    parent child depth
        A     A       0
        B     B       0
        A     B       1

    Hierarchy after adding the new node C (A -> B -> C):
    parent child depth
        A     A       0
        B     B       0
        A     B       1
        C     C       0  # reference to itself
        B     C       1  # reference to immediate parent
        A     C       2  # reference to parent with depth 2

    For more information on closure tables: https://fueled.com/the-cache/posts/backend/closure-table/#closure-table
    """
    PeopleFinderTeamTree.objects.bulk_create(
        [
            # Add a reference to the team itself
            PeopleFinderTeamTree(parent=team, child=team, depth=0),
            # Add all required tree connections
            *(
                # Here we add entries to the PeopleFinderTeamTree representing the depth and
                # relationships of the team (new team we are adding to the hierarchy) with each
                # of its parents, not only with its immediate parent! We set child=parent to get
                # ALL the parents of the team's immediate parent.
                PeopleFinderTeamTree(parent=tt.parent, child=team, depth=tt.depth + 1)
                for tt in PeopleFinderTeamTree.objects.filter(child=parent)
            ),
        ]
    )


def validate_team_parent_update(
    team: PeopleFinderTeam, parent: PeopleFinderTeam
) -> None:
    """Validate that the new parent is valid for the given team.

    Args:
        team (PeopleFinderTeam):The team to be updated.
        parent (PeopleFinderTeam): The given parent team.

    Raises:
        TeamParentError: If team's parent is not a valid parent.
    """
    if parent == team:
        raise TeamParentError("A team's parent cannot be the team itself")

    if parent in get_all_child_teams(team):
        raise TeamParentError("A team's parent cannot be a team's child")

    if parent and (team == get_root_team()):
        raise TeamParentError("Cannot update the parent of the root team")


@transaction.atomic
def update_team_parent(team: PeopleFinderTeam, parent: PeopleFinderTeam) -> None:
    """Update a team's parent with the given parent team.

    The implementation was informed by the following blog:
    https://www.percona.com/blog/2011/02/14/moving-subtrees-in-closure-table/

    Args:
        team (PeopleFinderTeam): The team to be updated.
        parent (PeopleFinderTeam): The given parent team.
    """
    validate_team_parent_update(team, parent)

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


@transaction.atomic
def remove_team_parent(team: PeopleFinderTeam) -> None:
    """
    Similar function to the update_team_parent function, but without excluding the self relationship and
    only deleting tree nodes without adding any new nodes to the tree.
    """
    PeopleFinderTeamTree.objects.filter(
        child__in=Subquery(
            PeopleFinderTeamTree.objects.filter(parent=team).values("child")
        )
    ).delete()


def get_all_parent_teams(child: PeopleFinderTeam) -> QuerySet[PeopleFinderTeam]:
    """Return all parent teams for the given child team.

    Args:
        child (PeopleFinderTeam): The given child team.

    Returns:
        QuerySet: A query of teams.
    """
    return (
        PeopleFinderTeam.objects.filter(parents__child=child).exclude(
            parents__parent=child
        )
        # TODO: Not sure if we should order here or at the call sites.
        .order_by("-parents__depth")
    )


def get_immediate_parent_team(child: PeopleFinderTeam) -> Optional[PeopleFinderTeam]:
    """Return the immediate parent team for the given team.

    Args:
        child (PeopleFinderTeam): The given team.

    Returns:
        PeopleFinderTeam: The immediate parent team.
    """
    try:
        return PeopleFinderTeam.objects.filter(
            parents__child=child, parents__depth=1
        ).get()
    except PeopleFinderTeam.DoesNotExist:
        return None


def get_all_child_teams(parent: PeopleFinderTeam) -> QuerySet[PeopleFinderTeam]:
    """Return all child teams of the given parent team.

    Args:
        parent (PeopleFinderTeam): The given parent team.

    Returns:
        QuerySet: A queryset of peoplefinder teams.
    """
    return PeopleFinderTeam.objects.filter(children__parent=parent).exclude(
        children__child=parent
    )


def get_immediate_child_teams(parent: PeopleFinderTeam) -> QuerySet[PeopleFinderTeam]:
    """Return all immediate child teams of the given parent team.

    Args:
        parent (PeopleFinderTeam): The given parent team.

    Returns:
        QuerySet: A queryset of peoplefinder teams.
    """
    return PeopleFinderTeam.objects.filter(children__parent=parent, children__depth=1)


def get_root_team() -> PeopleFinderTeam:
    """Return the root team.

    Returns:
        PeopleFinderTeam: The root team.
    """
    teams_with_parents = PeopleFinderTeamTree.objects.filter(depth__gt=0)

    return PeopleFinderTeam.objects.exclude(
        id__in=Subquery(teams_with_parents.values("child"))
    ).get()


def get_team_members(team: PeopleFinderTeam) -> QuerySet[PeopleFinderProfileTeam]:
    """
    Get all team members that are either active members of the current team or its children
    """
    sub_teams = get_all_child_teams(team)
    # Not sure about performance here as it's doing a inner query to check active status.
    return PeopleFinderProfileTeam.objects.filter(
        Q(team=team) | Q(team__in=sub_teams) & Q(peoplefinder_profile__is_active=True)
    )
