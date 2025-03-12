import uuid

import pytest
from django.contrib.admin.models import LogEntry
from django.core.exceptions import ValidationError

from profiles.exceptions import TeamExists
from profiles.models import PeopleFinderProfile
from profiles.models.generic import Grade, UkStaffLocation
from profiles.services import peoplefinder as peoplefinder_services
from profiles.types import UNSET
from user.models import User


pytestmark = pytest.mark.django_db


def test_create(peoplefinder_profile):
    # Create staff location
    UkStaffLocation.objects.create(
        code="test",
        name="test_name",
        city="test_city",
        organisation="test_organisation",
        building_name="test_building_name",
    )

    # Manager
    manager = peoplefinder_profile

    # User
    user = User.objects.create(sso_email_id="tom@email.com")

    peoplefinder_profile = peoplefinder_services.create(
        slug=str(uuid.uuid4()),
        user=user,
        is_active=user.is_active,
        first_name="Tom",
        last_name="Doe",
        email_address="tom@email.com",
        contact_email_address="tom_contact@email.com",
        grade=Grade("grade_7"),
        country_id="CTHMTC00260",
        uk_office_location_id="test",
        manager_slug=manager.slug,
    )

    assert peoplefinder_profile.first_name == "Tom"
    assert peoplefinder_profile.last_name == "Doe"
    assert peoplefinder_profile.grade == "grade_7"
    assert peoplefinder_profile.uk_office_location == UkStaffLocation.objects.get(
        code="test"
    )
    assert peoplefinder_profile.manager == manager


def test_update(peoplefinder_profile, combined_profile):
    # Check the first_name last_name and grade before update
    assert peoplefinder_profile.first_name == "John"
    assert peoplefinder_profile.last_name == "Doe"
    assert peoplefinder_profile.grade == "grade_7"

    peoplefinder_services.update(
        peoplefinder_profile=peoplefinder_profile,
        is_active=combined_profile.is_active,
        first_name="James",
        grade=UNSET,
    )
    # Check the first_name, last_name and grade after update
    assert peoplefinder_profile.first_name == "James"
    assert peoplefinder_profile.last_name == "Doe"
    assert peoplefinder_profile.is_active == combined_profile.is_active
    assert peoplefinder_profile.grade == None


def test_update_team(peoplefinder_team):

    # Check the team name, cost code and description before update
    assert peoplefinder_team.name == "Team1Name"
    assert peoplefinder_team.description == "Team description"
    assert peoplefinder_team.cost_code == "CC1"

    peoplefinder_services.update_team(
        peoplefinder_team=peoplefinder_team,
        name="New team name",
        description="New Team Description",
        cost_code=UNSET,
    )
    # Check the team name, cost code and description after update
    assert peoplefinder_team.name == "New team name"
    assert peoplefinder_team.description == "New Team Description"
    assert peoplefinder_team.cost_code is None


def test_delete_from_database(peoplefinder_profile):
    obj_repr = str(peoplefinder_profile)
    peoplefinder_profile.refresh_from_db()
    peoplefinder_services.delete_from_database(peoplefinder_profile)
    with pytest.raises(peoplefinder_profile.DoesNotExist):
        peoplefinder_services.get_by_slug(
            slug=peoplefinder_profile.slug, include_inactive=True
        )

    assert LogEntry.objects.count() == 1
    log = LogEntry.objects.first()
    assert log.is_deletion()
    assert log.user.pk == "via-api"
    assert log.object_repr == obj_repr
    assert log.get_change_message() == "Deleting People Finder Profile record"


def test_get_by_id(peoplefinder_profile):
    # Get an active people finder profile
    actual = peoplefinder_services.get_by_slug(slug=peoplefinder_profile.slug)
    assert actual.user.sso_email_id == peoplefinder_profile.user.sso_email_id

    # Get a soft-deleted people finder profile when inactive profiles are included
    peoplefinder_profile.is_active = False
    peoplefinder_profile.save()

    soft_deleted_profile = peoplefinder_services.get_by_slug(
        peoplefinder_profile.slug, include_inactive=True
    )
    assert soft_deleted_profile.is_active == False

    # Try to get a soft-deleted profile when inactive profiles are not included
    with pytest.raises(PeopleFinderProfile.DoesNotExist) as ex:
        # no custom error to keep overheads low
        peoplefinder_services.get_by_slug(slug=soft_deleted_profile.slug)

    assert ex.value.args[0] == "PeopleFinderProfile matching query does not exist."

    # Try to get a non-existent profile
    with pytest.raises(PeopleFinderProfile.DoesNotExist) as ex:
        peoplefinder_services.get_by_slug(slug="550e8400-e29b-41d4-a716-446655440000")
    assert str(ex.value.args[0]) == "PeopleFinderProfile matching query does not exist."


def test_get_countries():
    countries = peoplefinder_services.get_countries()
    # Check if country properties exist in fetched country
    expected = {
        "reference_id": "CTHMTC00260",
        "name": "UK",
        "type": "country",
        "iso_1_code": "31",
        "iso_2_code": "66",
        "iso_3_code": "2",
        "overseas_region": None,
        "start_date": None,
        "end_date": None,
    }
    assert expected.items() <= countries[0].__dict__.items()


def test_get_uk_staff_locations():
    locations = peoplefinder_services.get_uk_staff_locations()
    # Check if code, name, organisation and building_name exists in the location dict
    assert {
        "code": "location_1",
        "name": "OAB_UK",
        "organisation": "DBT",
        "building_name": "OAB",
    }.items() <= locations[0].__dict__.items()


def test_get_remote_working_options():
    options = peoplefinder_services.get_remote_working()
    assert options == [
        ("office_worker", "Office worker"),
        ("remote_worker", "Remote worker"),
        ("split", "Split"),
    ]


def test_get_workday_options():
    options = peoplefinder_services.get_workdays()

    assert options == [
        ("mon", "Monday"),
        ("tue", "Tuesday"),
        ("wed", "Wednesday"),
        ("thu", "Thursday"),
        ("fri", "Friday"),
        ("sat", "Saturday"),
        ("sun", "Sunday"),
    ]


def test_get_learning_interest_options():
    options = peoplefinder_services.get_learning_interests()

    assert options == [
        ("shadowing", "Work shadowing"),
        ("mentoring", "Mentoring"),
        ("research", "Research"),
        ("overseas_posts", "Overseas posts"),
        ("secondment", "Secondment"),
        ("parliamentary_work", "Parliamentary work"),
        ("ministerial_submissions", "Ministerial submissions"),
        ("coding", "Coding"),
    ]


def test_get_professions():
    options = peoplefinder_services.get_professions()

    assert options == [
        ("commercial", "Government commercial and contract management"),
        ("corp_finance", "Corporate finance profession"),
        ("counter_fraud", "Counter-fraud standards and profession"),
        ("digital_data_tech", "Digital, data and technology profession"),
        ("gov_comms", "Government communication service"),
        ("gov_economics", "Government economic service"),
        ("gov_finance", "Government finance profession"),
        ("gov_it", "Government IT profession"),
        ("gov_knowledge", "Government knowledge and information management profession"),
        ("gov_legal", "Government legal service"),
        ("gov_occupational", "Government occupational psychology profession"),
        ("gov_operational", "Government operational research service"),
        ("gov_planning_inspectors", "Government planning inspectors"),
        ("gov_planning_profession", "Government planning profession"),
        ("gov_property", "Government property profession"),
        ("gov_security", "Government security profession"),
        ("gov_science", "Government science and engineering profession"),
        ("gov_social", "Government social research profession"),
        ("gov_statistical", "Government statistical service profession"),
        ("gov_tax", "Government tax profession"),
        ("gov_vet", "Government veterinary profession"),
        ("human_resources", "Human resources profession"),
        ("intelligence_analysis", "Intelligence analysis"),
        ("internal_audit", "Internal audit profession"),
        ("medical_profession", "Medical profession"),
        ("operation_delivery", "Operational delivery profession"),
        ("policy_profiession", "Policy profession"),
        ("procurement_profession", "Procurement profession"),
        ("project_delivery", "Project delivery profession"),
        ("international_trade", "International trade profession"),
    ]


def test_get_key_skills():
    options = peoplefinder_services.get_key_skills()

    assert options == [
        ("asset_management", "Asset management"),
        ("assurance", "Assurance"),
        ("benefits_realisation", "Benefits realisation"),
        ("change_management", "Change management"),
        ("coaching", "Coaching"),
        ("commercial_specialist", "Commercial specialist"),
        ("commissioning", "Commissioning"),
        ("contract_management", "Contract management"),
        ("credit_risk_analysis", "Credit risk analysis"),
        ("customer_service", "Customer service"),
        ("digital", "Digital"),
        ("digital_workspace_publisher", "Digital Workspace publisher"),
        ("economist", "Economist"),
        ("financial_reporting", "Financial reporting"),
        ("graphic_design", "Graphic Design"),
        ("hr", "HR"),
        ("income_generation", "Income generation"),
        ("information_management", "Information management"),
        ("interviewing", "Interviewing"),
        ("it", "IT"),
        ("law", "Law"),
        ("lean", "Lean/ Six sigma"),
        ("line_management", "Line management"),
        ("media_trained", "Media trained"),
        ("mentoring", "Mentoring"),
        ("policy_design", "Policy design"),
        ("policy_implementation", "Policy implementation"),
        ("presenting", "Presenting"),
        ("project_delivery", "Project delivery"),
        ("project_management", "Project management"),
        ("property_estates", "Property / Estates"),
        ("research_operational", "Research - operational"),
        ("research_economic", "Research - economic"),
        ("research_statistical", "Research - statistical"),
        ("research_social", "Research - social"),
        ("risk_management", "Risk management"),
        ("security", "Security"),
        ("service_design", "Service and process design"),
        ("skills_and_capability", "Skills and capability management"),
        ("sponsorship", "Sponsorship and partnerships"),
        ("stakeholder_management", "Stakeholder management"),
        ("statistics", "Statistics"),
        ("strategy", "Strategy"),
        ("submission_writing", "Submission writing"),
        ("talent_management", "Talent Management"),
        ("tax", "Tax"),
        ("training", "Training"),
        ("underwriting", "Underwriting"),
        ("user_research", "User research"),
        ("valution", "Valuation"),
        ("working_with_devolved_admin", "Working with Devolved Administrations"),
        ("working_with_ministers", "Working with Ministers"),
        ("working_with_govt_depts", "Working with other government departments"),
    ]


def test_get_grades():
    options = peoplefinder_services.get_grades()
    assert options == [
        ("fco_s1", "FCO S1"),
        ("fco_s2", "FCO S2"),
        ("fco_s3", "FCO S3"),
        ("admin_assistant", "Administrative assistant (AA)"),
        ("admin_officer", "Administrative officer (AO/A2)"),
        ("executive_officer", "Executive officer (EO/B3)"),
        ("higher_executive_officer", "Higher executive officer (HEO/C4)"),
        ("senior_executive_officer", "Senior executive officer (SEO/C5)"),
        ("grade_7", "Grade 7 (G7/D6)"),
        ("grade_6", "Grade 6 (G6/D7)"),
        ("scs_1", "Senior civil service 1 (SCS1/SMS1)"),
        ("scs_2", "Senior civil service 2 (SCS2/SMS2)"),
        ("scs_3", "Senior civil service 3 (SCS3/SMS3)"),
        ("scs_4", "Senior civil service 4 (SCS4/SMS4)"),
        ("fast_stream", "Fast Stream"),
        ("fast_track", "Fast Track"),
        ("apprentice", "Apprentice"),
        ("non_graded_special_advisor", "Non graded - special advisor (SPAD)"),
        ("non_graded_contractor", "Non graded - contractor"),
        ("non_graded_secondee", "Non graded - secondee"),
        ("non_graded_post", "Non graded - post"),
    ]


def test_get_additional_roles():
    options = peoplefinder_services.get_additional_roles()
    assert options == [
        ("fire_warden", "Fire warden"),
        ("first_aider", "First aider"),
        ("mental_health_first_aider", "Mental health first aider"),
        ("mentor", "Mentor"),
        ("network_lead", "Network lead"),
        ("network_deputy_lead", "Network deputy lead"),
        ("cirrus_champion", "Cirrus champion"),
        ("health_wellbeing_champion", "Health & wellbeing champion"),
        ("fast_stream_rep", "Fast stream rep"),
        ("overseas_staff_rep", "Overseas staff rep"),
        ("digital_champion", "Digital champion"),
        ("information_manager", "Information manager"),
        ("independent_panel_member", "Independent panel member"),
        ("divisional_security_coordinator", "Divisional security coordinator"),
        ("ddat_champion", "DDaT champion"),
        ("honours_champion", "Honours champion"),
    ]


def test_create_team():
    # Create a peoplefinder team
    peoplefinder_services.create_team(
        slug="employee-experience",
        name="Employee Experience",
        abbreviation="EX",
        description="We support the platforms, products, tools and services that help our colleagues to do their jobs.",
        leaders_ordering="custom",
        cost_code="EX_cost_code",
        team_type="portfolio",
    )

    # Try to create a team with the same slug
    with pytest.raises(TeamExists) as ex:
        peoplefinder_services.create_team(
            slug="employee-experience",
            name="Employees' Experiences",
            abbreviation="EXs",
            description="We support employees' experiences",
            leaders_ordering="alphabetical",
            cost_code="EXs_cost_code",
            team_type="portfolio",
        )

    assert ex.value.args[0] == "Team has been previously created"

    # Try to create a team with a wrong team type
    with pytest.raises(ValidationError):
        peoplefinder_services.create_team(
            slug="software-development",
            name="Software Development",
            abbreviation="SD",
            description="We build, maintain, and support a growing number of services in DBT",
            leaders_ordering="alphabetical",
            cost_code="SD_cost_code",
            team_type="Folio",
        )
