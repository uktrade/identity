from typing import Optional

from django.db import connection, transaction
from django.db.models import Q, QuerySet, Subquery
from django.utils.text import slugify

from profiles.exceptions import (
    ParentTeamDoesNotExist,
    TeamChildError,
    TeamExists,
    TeamMemberError,
    TeamParentError,
    TeamRootError,
    TeamSlugError,
)
from profiles.models.peoplefinder import (
    PeopleFinderHierarchyData,
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
    parent: PeopleFinderTeam,
    leaders_ordering: Optional[PeopleFinderTeamLeadersOrdering],
    team_type: Optional[PeopleFinderTeamType],
    abbreviation: Optional[str] = None,
    description: Optional[str] = None,
    cost_code: Optional[str] = None,
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
    team: PeopleFinderTeam,
    slug: Optional[str] = None,
    name: Optional[str] = None,
    abbreviation: Optional[str | Unset] = None,
    description: Optional[str | Unset] = None,
    leaders_ordering: Optional[PeopleFinderTeamLeadersOrdering | Unset] = None,
    cost_code: Optional[str | Unset] = None,
    team_type: Optional[PeopleFinderTeamType | Unset] = None,
    parent: Optional[PeopleFinderTeam] = None,
) -> None:
    """
    Updates a people finder team
    """
    update_fields: list = []

    # Update fields that are required on the PeopleFinderTeam
    if name:
        team.name = name
        update_fields.append("name")

    # Update fields that are optional on the PeopleFinderTeam
    if abbreviation is not None:
        if abbreviation is UNSET:
            team.abbreviation = None
        else:
            team.abbreviation = abbreviation
        update_fields.append("abbreviation")
    if description is not None:
        if description is UNSET:
            team.description = None
        else:
            team.description = description
        update_fields.append("description")
    if leaders_ordering is not None:
        if leaders_ordering is UNSET:
            team.leaders_ordering = None
        else:
            team.leaders_ordering = leaders_ordering
        update_fields.append("leaders_ordering")
    if cost_code is not None:
        if cost_code is UNSET:
            team.cost_code = None
        else:
            team.cost_code = cost_code
        update_fields.append("cost_code")
    if team_type is not None:
        if team_type is UNSET:
            team.team_type = None
        else:
            team.team_type = team_type
        update_fields.append("team_type")

    # Validate fields and update team parent before saving the team updates
    if parent:
        update_team_parent(team=team, parent=parent)

    # Update team slug after updating the parent in the team tree
    if slug:
        team.slug = generate_team_slug(value=slug, team=team)
        update_fields.append("slug")
    elif name:
        team.slug = generate_team_slug(value=name, team=team)
        update_fields.append("slug")

    team.full_clean()
    team.save(update_fields=update_fields)


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


def get_team_hierarchy() -> PeopleFinderHierarchyData:
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

    def build_team_node(team) -> PeopleFinderHierarchyData:
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
        "description": team.description,
        "leaders_ordering": team.leaders_ordering,
        "cost_code": team.cost_code,
        "team_type": team.team_type,
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


def generate_team_slug(team: PeopleFinderTeam, value: str) -> str:
    """Return a new slug for the given team.

    Args:
        team (PeopleFinderTeam): The given team.
        value: slug or name field value

    Raises:
        TeamSlugError: If a unique team slug cannot be generated.

    Returns:
        str: A new slug for the PeopleFinderTeam.
    """
    new_slug = slugify(value)

    duplicate_slugs = (
        PeopleFinderTeam.objects.filter(slug=new_slug).exclude(pk=team.pk).exists()
    )

    # If the new slug isn't unique then append the parent team's name to the front.
    # Note that if the parent team's name changes it won't be reflected here in the
    # new slug.
    if duplicate_slugs:
        parent_team = get_immediate_parent_team(team)

        if not parent_team:
            raise TeamSlugError(
                "Cannot generate unique slug as the team is the root team"
            )

        new_slug = slugify(f"{parent_team.name} {new_slug}")

    return new_slug


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
