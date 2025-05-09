import datetime as dt
from unittest.mock import call

import pytest

from core import services
from core.services import (
    SSO_CONTACT_EMAIL_ADDRESS,
    SSO_EMAIL_ADDRESSES,
    SSO_FIRST_NAME,
    SSO_LAST_NAME,
    SSO_USER_EMAIL_ID,
    SSO_USER_STATUS,
)
from profiles import services as profile_services
from profiles.exceptions import (
    TeamChildError,
    TeamExists,
    TeamMemberError,
    TeamRootError,
)
from profiles.models import PeopleFinderProfile
from profiles.models.combined import Profile
from profiles.models.generic import Country, Email
from profiles.models.peoplefinder import (
    PeopleFinderProfileTeam,
    PeopleFinderTeam,
    PeopleFinderTeamLeadersOrdering,
    PeopleFinderTeamTree,
    PeopleFinderTeamType,
)
from profiles.models.staff_sso import StaffSSOProfile
from profiles.services import staff_sso as sso_profile_services
from profiles.services.peoplefinder import profile as peoplefinder_services
from user import services as user_services
from user.exceptions import UserExists
from user.models import User


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("basic_user", [None])
def test_create_identity(mocker):
    mock_user_create = mocker.patch("user.services.create")
    mock_profiles_create = mocker.patch(
        "profiles.services.create_from_sso",
        return_value="__profile__",
    )
    # User is created
    profile = services.create_identity(
        id="billy.sso.email.id@gov.uk",
        first_name="Billy",
        last_name="Bob",
        all_emails=[
            "test@test.com",
            "test2@test.com",
            "test3@test.com",
        ],
        is_active=False,
        primary_email="test2@test.com",
        contact_email="test3@test.com",
    )
    mock_user_create.assert_called_once_with(
        sso_email_id="billy.sso.email.id@gov.uk",
        is_active=False,
    )
    mock_profiles_create.assert_called_once_with(
        sso_email_id="billy.sso.email.id@gov.uk",
        first_name="Billy",
        last_name="Bob",
        all_emails=[
            "test@test.com",
            "test2@test.com",
            "test3@test.com",
        ],
        primary_email="test2@test.com",
        contact_email="test3@test.com",
    )
    assert profile == "__profile__"


def test_existing_user(basic_user) -> None:
    with pytest.raises(UserExists):
        services.create_identity(
            id=basic_user.pk,
            first_name="Billy",
            last_name="Bob",
            all_emails=["new_user@email.gov.uk"],
            is_active=True,
        )


def test_new_user() -> None:
    profile = services.create_identity(
        id="new_user@gov.uk",
        first_name="Billy",
        last_name="Bob",
        all_emails=["new_user@email.gov.uk"],
        is_active=True,
    )
    assert isinstance(profile, Profile)
    assert profile.pk
    assert profile.sso_email_id == "new_user@gov.uk"
    assert user_services.get_by_id(
        sso_email_id="new_user@gov.uk", include_inactive=True
    )


def test_update_identity() -> None:
    profile = services.create_identity(
        "new_user@gov.uk",
        "Billy",
        "Bob",
        ["new_user@email.gov.uk"],
        is_active=True,
    )
    assert user_services.get_by_id(
        sso_email_id="new_user@gov.uk", include_inactive=True
    ).is_active

    services.update_identity(
        profile,
        first_name="Joe",
        last_name="Bobby",
        all_emails=["new_user@email.gov.uk"],
        is_active=False,
    )
    profile.refresh_from_db()

    assert profile.first_name == "Joe"
    assert profile.last_name == "Bobby"
    assert not user_services.get_by_id(
        sso_email_id="new_user@gov.uk",
        include_inactive=True,
    ).is_active


def test_delete_identity() -> None:
    profile = services.create_identity(
        id="new_user@gov.uk",
        first_name="Billy",
        last_name="Bob",
        all_emails=["new_user@email.gov.uk"],
        is_active=True,
    )

    user = User.objects.get(sso_email_id=profile.sso_email_id)
    PeopleFinderProfile.objects.create(
        user=user,
        workdays=["Monday, Tuesday"],
        professions=["COMMERCIAL"],
        additional_roles=["FIRE_WARDEN"],
        key_skills=["ASSET_MANAGEMENT"],
        learning_interests=["SHADOWING"],
        edited_or_confirmed_at=dt.datetime.now(),
    )

    services.delete_identity(
        profile,
    )
    with pytest.raises(Profile.DoesNotExist) as pex:
        services.get_identity_by_id(
            id=profile.sso_email_id,
            include_inactive=True,
        )

    assert str(pex.value.args[0]) == "Profile matching query does not exist."

    # check that people finder profile has been deleted
    with pytest.raises(PeopleFinderProfile.DoesNotExist) as pfex:
        PeopleFinderProfile.objects.get(
            user__sso_email_id=user.sso_email_id,
        )
    assert (
        str(pfex.value.args[0]) == "PeopleFinderProfile matching query does not exist."
    )

    # check that sso profile has been deleted
    with pytest.raises(StaffSSOProfile.DoesNotExist) as pfex:
        sso_profile_services.get_by_id(
            sso_email_id=user.sso_email_id,
            include_inactive=True,
        )
    assert str(pfex.value.args[0]) == "StaffSSOProfile matching query does not exist."

    with pytest.raises(User.DoesNotExist) as uex:
        user_services.get_by_id(
            sso_email_id="new_user@gov.uk",
            include_inactive=True,
        )

    assert str(uex.value.args[0]) == "User does not exist"


def test_update_peoplefinder_profile(combined_profile, peoplefinder_profile, manager):
    # Create a new country to update the existing one
    Country.objects.create(
        reference_id="country2",
        name="country2",
        type="country",
        iso_1_code="33",
        iso_2_code="63",
        iso_3_code="23",
    )

    services.update_peoplefinder_profile(
        profile=combined_profile,
        slug=peoplefinder_profile.slug,
        is_active=combined_profile.is_active,
        email_address="new_super_fancy_email@gov.uk",
        country_id="country2",
        uk_office_location_id="location_1",
        manager_slug=manager.slug,
    )

    peoplefinder_profile.refresh_from_db()
    assert peoplefinder_profile.email.address == "new_super_fancy_email@gov.uk"
    assert peoplefinder_profile.country.reference_id == "country2"
    assert peoplefinder_profile.uk_office_location.code == "location_1"
    assert peoplefinder_profile.manager == manager

    # Delete identity and try to update the peoplefinder profile
    services.delete_identity(profile=combined_profile)

    with pytest.raises(PeopleFinderProfile.DoesNotExist):
        services.update_peoplefinder_profile(
            profile=combined_profile,
            slug=peoplefinder_profile.slug,
            is_active=combined_profile.is_active,
            email_address="new_super_fancy_email@gov.uk",
            country_id="country2",
            uk_office_location_id="location_1",
            manager_slug=manager.slug,
        )


def test_create_peoplefinder_team_core_services(peoplefinder_team):
    # Create a peoplefinder team
    services.create_peoplefinder_team(
        slug="employee-experience",
        name="Employee Experience",
        abbreviation="EX",
        description="We support the platforms, products, tools and services that help our colleagues to do their jobs.",
        leaders_ordering=PeopleFinderTeamLeadersOrdering("custom"),
        cost_code="EX_cost_code",
        team_type=PeopleFinderTeamType("portfolio"),
        parent=peoplefinder_team,
    )

    ex_team = PeopleFinderTeam.objects.get(slug="employee-experience")
    ex_in_team_tree = PeopleFinderTeamTree.objects.filter(child=ex_team)
    # Check if EX team entries are added to the team tree
    assert set(ex_in_team_tree).issubset(set(PeopleFinderTeamTree.objects.all()))

    # Try to create a team with the same slug
    with pytest.raises(TeamExists) as ex:
        services.create_peoplefinder_team(
            slug="employee-experience",
            name="Employees' Experiences",
            abbreviation="EXs",
            description="We support employees' experiences",
            leaders_ordering=PeopleFinderTeamLeadersOrdering("alphabetical"),
            cost_code="EXs_cost_code",
            team_type=PeopleFinderTeamType("portfolio"),
            parent=peoplefinder_team,
        )

    assert ex.value.args[0] == "Team has been previously created"


def test_update_peoplefinder_team(peoplefinder_team):
    services.update_peoplefinder_team(
        team=peoplefinder_team,
        slug=None,
        name="New Name",
        abbreviation="NABV",
        description="New Desc",
        leaders_ordering=PeopleFinderTeamLeadersOrdering("custom"),
        cost_code="CC123",
        team_type=PeopleFinderTeamType("directorate"),
    )

    peoplefinder_team.refresh_from_db()
    assert peoplefinder_team.name == "New Name"
    assert peoplefinder_team.slug == "new-name"
    assert peoplefinder_team.abbreviation == "NABV"
    assert peoplefinder_team.description == "New Desc"
    assert peoplefinder_team.cost_code == "CC123"
    assert peoplefinder_team.leaders_ordering == "custom"
    assert peoplefinder_team.team_type == "directorate"


def test_delete_peoplefinder_team(peoplefinder_team):
    """
    Test deletion of a peoplefinder team
    """
    team_to_delete = services.create_peoplefinder_team(
        slug="test-1",
        name="test-1",
        abbreviation="tr-1",
        description="test-1",
        leaders_ordering=PeopleFinderTeamLeadersOrdering("alphabetical"),
        cost_code="test-1",
        team_type=PeopleFinderTeamType("standard"),
        parent=peoplefinder_team,
    )

    services.delete_peoplefinder_team(slug=team_to_delete.slug)

    with pytest.raises(PeopleFinderTeam.DoesNotExist) as pex:
        team_to_delete.refresh_from_db()

    assert str(pex.value.args[0]) == "PeopleFinderTeam matching query does not exist."

    assert peoplefinder_team.name == "Root team"
    assert peoplefinder_team.abbreviation == "RT"
    assert peoplefinder_team.description == None
    assert peoplefinder_team.cost_code == None
    assert (
        peoplefinder_team.leaders_ordering
        == PeopleFinderTeamLeadersOrdering.ALPHABETICAL
    )
    assert peoplefinder_team.team_type == PeopleFinderTeamType.STANDARD


def test_delete_peoplefinder_root_team(peoplefinder_team):
    """
    Test deletion fails when deleting the root team.
    """

    with pytest.raises(TeamRootError) as pex:
        services.delete_peoplefinder_team(slug=peoplefinder_team.slug)

    assert str(pex.value.args[0]) == "Cannot delete the root team"


def test_delete_peoplefinder_team_active_members(
    peoplefinder_profile, peoplefinder_team
):
    """
    Test deletion fails when deleting a team that has active members
    """
    team_to_delete = services.create_peoplefinder_team(
        slug="test-1",
        name="test-1",
        abbreviation="tr-1",
        description="test-1",
        leaders_ordering=PeopleFinderTeamLeadersOrdering("alphabetical"),
        cost_code="test-1",
        team_type=PeopleFinderTeamType("standard"),
        parent=peoplefinder_team,
    )

    # TODO add missing service methods
    # Manually adding a profile to a team, the method(s) has not been created yet.
    PeopleFinderProfileTeam.objects.create(
        peoplefinder_profile=peoplefinder_profile,
        team=team_to_delete,
        job_title="Test Job",
    )

    with pytest.raises(TeamMemberError) as pex:
        services.delete_peoplefinder_team(slug=team_to_delete.slug)

    assert str(pex.value.args[0]) == "Cannot delete a team that contains active members"


def test_delete_peoplefinder_team_has_sub_teams(peoplefinder_team):
    """
    Test deletion fails when deleting a team that has sub teams
    """

    team_to_delete = services.create_peoplefinder_team(
        slug="test-1",
        name="test-1",
        abbreviation="tr-1",
        description="test-1",
        leaders_ordering=PeopleFinderTeamLeadersOrdering("alphabetical"),
        cost_code="test-1",
        team_type=PeopleFinderTeamType("standard"),
        parent=peoplefinder_team,
    )

    # create sub team
    services.create_peoplefinder_team(
        slug="test-2",
        name="test-2",
        abbreviation="tr-2",
        description="test-2",
        leaders_ordering=PeopleFinderTeamLeadersOrdering("alphabetical"),
        cost_code="test-2",
        team_type=PeopleFinderTeamType("standard"),
        parent=team_to_delete,
    )

    with pytest.raises(TeamChildError) as pex:
        services.delete_peoplefinder_team(slug=team_to_delete.slug)

    assert str(pex.value.args[0]) == "Cannot delete a team that contains children"
