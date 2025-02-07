from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from ninja import Schema


@dataclass
class User:
    sso_email_id: str
    is_staff: bool = False
    is_active: bool = True


@dataclass
class Email:
    value: str
    type: str | None = None
    primary: bool = False


@dataclass
class Country:
    reference_id: str
    name: str
    type: Optional[str]
    iso_1_code: Optional[str]
    iso_2_code: Optional[str]
    iso_3_code: Optional[str]
    overseas_region: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created: Optional[datetime]
    modified: Optional[datetime]
    is_not_deleted_upstream: Optional[bool]


@dataclass
class UkStaffLocation:
    code: Optional[str]
    name: Optional[str]
    city: Optional[str]
    organisation: Optional[str]
    building_name: Optional[str]
    created: Optional[datetime]
    modified: Optional[datetime]
    is_not_deleted_upstream: Optional[bool]


class MinimalPeopleFinderProfile(Schema):
    # Basic Profile info
    slug: str
    user: Optional[User]  # ForeignKey to "user.User"
    first_name: str
    preferred_first_name: Optional[str]
    last_name: str
    pronouns: Optional[str]
    name_pronunciation: Optional[str]
    email: Optional[Email]  # ForeignKey to "profiles.Email"
    contact_email: Optional[Email]  # ForeignKey to "profiles.Email"
    primary_phone_number: Optional[str]
    secondary_phone_number: Optional[str]
    photo: Optional[str]  # ImageField is represented as a string (file path or URL)
    photo_small: Optional[
        str
    ]  # ImageField is represented as a string (file path or URL)
    grade: Optional[str]


class PeopleFinderProfileSchema(Schema):
    # Basic Profile info
    slug: str
    user: Optional[User]  # ForeignKey to "user.User"
    first_name: str
    preferred_first_name: Optional[str]
    last_name: str
    pronouns: Optional[str]
    name_pronunciation: Optional[str]
    email: Optional[Email]  # ForeignKey to "profiles.Email"
    contact_email: Optional[Email]  # ForeignKey to "profiles.Email"
    primary_phone_number: Optional[str]
    secondary_phone_number: Optional[str]
    photo: Optional[str]
    photo_small: Optional[str]

    # HR information
    grade: Optional[str]
    manager: Optional[MinimalPeopleFinderProfile]
    not_employee: bool

    # Working patterns
    workdays: Optional[List[str]]
    remote_working: Optional[str]
    usual_office_days: Optional[str]
    uk_office_location: Optional[UkStaffLocation]
    location_in_building: Optional[str]
    international_building: Optional[str]
    country: Optional[Country]

    # Supplementary info
    professions: Optional[List[str]]
    additional_roles: Optional[List[str]]
    other_additional_roles: Optional[str]
    key_skills: Optional[List[str]]
    other_key_skills: Optional[str]
    learning_interests: Optional[List[str]]
    other_learning_interests: Optional[str]
    fluent_languages: Optional[str]
    intermediate_languages: Optional[str]
    previous_experience: Optional[str]

    # Metadata and status
    is_active: Optional[bool]
    became_inactive: Optional[datetime]
    edited_or_confirmed_at: datetime
    login_count: Optional[int]
    profile_completion: Optional[int]
    ical_token: Optional[str]


class PeopleFinderTeamSchema(Schema):
    slug: str
    name: Optional[str]
    abbreviation: Optional[str]
    description: Optional[str]
    leaders_ordering: Optional[str]
    cost_code: Optional[str]
    team_type: Optional[str]
    short_name: Optional[str]


class PeopleFinderProfileTeamSchema(Schema):
    id: int
    peoplefinder_profile: PeopleFinderProfileSchema
    team: PeopleFinderTeamSchema
    job_title: Optional[str]
    head_of_team: Optional[bool]
    leaders_position: Optional[int]


class PeopleFinderTeamTreeSchema(Schema):
    parent_id: PeopleFinderTeamSchema
    child_id: PeopleFinderTeamSchema
    depth: int
