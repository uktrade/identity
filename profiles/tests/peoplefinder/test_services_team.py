import unittest

import pytest
from django.core.exceptions import ValidationError

from profiles.exceptions import TeamExists, TeamParentError
from profiles.models.peoplefinder import PeopleFinderTeam, PeopleFinderTeamTree
from profiles.services.peoplefinder import team as peoplefinder_team_services
from profiles.types import UNSET


pytestmark = pytest.mark.django_db


def test_create_team(peoplefinder_team):
    # Create a peoplefinder team
    peoplefinder_team_services.create(
        slug="employee-experience",
        name="Employee Experience",
        abbreviation="EX",
        description="We support the platforms, products, tools and services that help our colleagues to do their jobs.",
        leaders_ordering="custom",
        cost_code="EX_cost_code",
        team_type="portfolio",
        parent=peoplefinder_team,
    )

    # Try to create a team with the same slug
    with pytest.raises(TeamExists) as ex:
        peoplefinder_team_services.create(
            slug="employee-experience",
            name="Employees' Experiences",
            abbreviation="EXs",
            description="We support employees' experiences",
            leaders_ordering="alphabetical",
            cost_code="EXs_cost_code",
            team_type="portfolio",
            parent=peoplefinder_team,
        )

    assert ex.value.args[0] == "Team has been previously created"

    # Try to create a team with a wrong team type
    with pytest.raises(ValidationError):
        peoplefinder_team_services.create(
            slug="software-development",
            name="Software Development",
            abbreviation="SD",
            description="We build, maintain, and support a growing number of services in DBT",
            leaders_ordering="alphabetical",
            cost_code="SD_cost_code",
            team_type="Folio",
            parent=peoplefinder_team,
        )


def test_update_team(peoplefinder_team):
    dit = peoplefinder_team_services.create(
        slug="dit",
        name="DIT",
        abbreviation="DIT",
        description="DIT team",
        leaders_ordering="custom",
        cost_code="cost_code",
        team_type="standard",
        parent=peoplefinder_team,
    )
    ex = peoplefinder_team_services.create(
        slug="employee-experience",
        name="Employee Experience",
        abbreviation="EX",
        description="We support the platforms, products, tools and services that help our colleagues to do their jobs.",
        leaders_ordering="custom",
        cost_code="EX_cost_code",
        team_type="portfolio",
        parent=peoplefinder_team,
    )
    # Check team hierarchy before updating the parent
    old_hierarchy = peoplefinder_team_services.get_team_hierarchy()
    assert old_hierarchy == {
        "slug": peoplefinder_team.slug,
        "name": peoplefinder_team.name,
        "abbreviation": peoplefinder_team.abbreviation,
        "children": [
            {
                "slug": dit.slug,
                "name": dit.name,
                "abbreviation": dit.abbreviation,
                "children": [],
            },
            {
                "slug": ex.slug,
                "name": ex.name,
                "abbreviation": ex.abbreviation,
                "children": [],
            },
        ],
    }

    peoplefinder_team_services.update(
        peoplefinder_team=ex,
        name="New team name",
        description="New Team Description",
        cost_code=UNSET,
        parent=dit,
    )

    # Check the team name, cost code and description after update
    assert ex.name == "New team name"
    assert ex.description == "New Team Description"
    assert ex.cost_code is None

    # Check new hierarchy after updating the parent
    new_hierarchy = peoplefinder_team_services.get_team_hierarchy()
    assert new_hierarchy == {
        "slug": peoplefinder_team.slug,
        "name": peoplefinder_team.name,
        "abbreviation": peoplefinder_team.abbreviation,
        "children": [
            {
                "slug": dit.slug,
                "name": dit.name,
                "abbreviation": dit.abbreviation,
                "children": [
                    {
                        "slug": ex.slug,
                        "name": ex.name,
                        "abbreviation": ex.abbreviation,
                        "children": [],
                    }
                ],
            }
        ],
    }


def test_get_team_hierarchy(peoplefinder_team):
    # Add a child node with depth 1 to the root team
    ex = peoplefinder_team_services.create(
        slug="employee-experience",
        name="Employee Experience",
        abbreviation="EX",
        description="We support the platforms, products, tools and services that help our colleagues to do their jobs.",
        leaders_ordering="custom",
        cost_code="EX_cost_code",
        team_type="portfolio",
        parent=peoplefinder_team,
    )
    # Add a child node with depth 2 to the root team
    id = peoplefinder_team_services.create(
        slug="identity",
        name="Identity Team",
        abbreviation="ID",
        description="We are building the ID service",
        leaders_ordering="custom",
        cost_code="EX_cost_code",
        team_type="standard",
        parent=ex,
    )

    hierarchy = peoplefinder_team_services.get_team_hierarchy()
    assert hierarchy == {
        "slug": peoplefinder_team.slug,
        "name": peoplefinder_team.name,
        "abbreviation": peoplefinder_team.abbreviation,
        "children": [
            {
                "slug": ex.slug,
                "name": ex.name,
                "abbreviation": ex.abbreviation,
                "children": [
                    {
                        "slug": id.slug,
                        "name": id.name,
                        "abbreviation": id.abbreviation,
                        "children": [],
                    }
                ],
            }
        ],
    }


def test_get_team_and_parents(peoplefinder_team):
    # Create child team
    ex = peoplefinder_team_services.create(
        slug="employee-experience",
        name="Employee Experience",
        abbreviation="EX",
        description="We support the platforms, products, tools and services that help our colleagues to do their jobs.",
        leaders_ordering="custom",
        cost_code="EX_cost_code",
        team_type="portfolio",
        parent=peoplefinder_team,
    )

    team_data = peoplefinder_team_services.get_team_and_parents(team=ex)

    assert team_data == {
        "slug": ex.slug,
        "name": ex.name,
        "abbreviation": ex.abbreviation,
        "children": None,
        "parents": [
            {
                "slug": peoplefinder_team.slug,
                "name": peoplefinder_team.name,
                "abbreviation": peoplefinder_team.abbreviation,
                "depth": 1,
            }
        ],
    }


# TODO: Write separate tests for each function.
# Test TeamService
def test_team_service(db):
    """
    .
    └── DIT
        ├── COO
        │   ├── Analysis
        │   └── Change
        └── GTI
            └── DEFEND
            ├── Investment
    """
    test_case = unittest.TestCase()

    # We need to start from fresh for these tests.
    PeopleFinderTeam.objects.all().delete()

    dit = PeopleFinderTeam.objects.create(name="DIT", slug="dit")
    coo = PeopleFinderTeam.objects.create(name="COO", slug="coo")
    gti = PeopleFinderTeam.objects.create(name="GTI", slug="gti")
    peoplefinder_team_services.add_team_to_teamtree(team=dit, parent=dit)
    peoplefinder_team_services.add_team_to_teamtree(team=coo, parent=dit)
    peoplefinder_team_services.add_team_to_teamtree(team=gti, parent=dit)

    coo_analysis = PeopleFinderTeam.objects.create(name="Analysis", slug="analysis")
    coo_change = PeopleFinderTeam.objects.create(name="Change", slug="change")
    peoplefinder_team_services.add_team_to_teamtree(team=coo_analysis, parent=coo)
    peoplefinder_team_services.add_team_to_teamtree(team=coo_change, parent=coo)

    gti_investment = PeopleFinderTeam.objects.create(
        name="Investment", slug="investment"
    )
    gti_defence = PeopleFinderTeam.objects.create(name="DEFEND", slug="defend")
    peoplefinder_team_services.add_team_to_teamtree(team=gti_investment, parent=gti)
    peoplefinder_team_services.add_team_to_teamtree(team=gti_defence, parent=gti)

    test_case.assertCountEqual(
        list(peoplefinder_team_services.get_all_child_teams(parent=dit)),
        [
            coo,
            gti,
            coo_analysis,
            coo_change,
            gti_investment,
            gti_defence,
        ],
    )

    test_case.assertCountEqual(
        list(peoplefinder_team_services.get_immediate_child_teams(parent=dit)),
        [coo, gti],
    )

    test_case.assertCountEqual(
        list(peoplefinder_team_services.get_all_parent_teams(child=coo_change)),
        [dit, coo],
    )

    assert peoplefinder_team_services.get_root_team() == dit

    assert peoplefinder_team_services.get_immediate_parent_team(gti_defence) == gti

    # test update
    peoplefinder_team_services.update_team_parent(gti, coo)

    assert peoplefinder_team_services.get_immediate_parent_team(gti) == coo

    test_case.assertCountEqual(
        list(peoplefinder_team_services.get_all_child_teams(coo)),
        [
            gti,
            coo_analysis,
            coo_change,
            gti_investment,
            gti_defence,
        ],
    )

    test_case.assertCountEqual(
        list(peoplefinder_team_services.get_immediate_child_teams(dit)), [coo]
    )

    # revert update
    peoplefinder_team_services.update_team_parent(gti, dit)

    assert peoplefinder_team_services.get_immediate_parent_team(gti) == dit

    # test `validate_team_parent_update` through `update_team_parent`
    with pytest.raises(
        TeamParentError, match="A team's parent cannot be the team itself"
    ):
        peoplefinder_team_services.update_team_parent(gti, gti)

    with pytest.raises(
        TeamParentError, match="A team's parent cannot be a team's child"
    ):
        peoplefinder_team_services.update_team_parent(gti, gti_investment)

    with pytest.raises(
        TeamParentError, match="Cannot update the parent of the root team"
    ):
        peoplefinder_team_services.update_team_parent(
            dit, PeopleFinderTeam(name="Test")
        )
