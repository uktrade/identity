from typing import Optional

from ninja import Field, Schema

from profiles.models.peoplefinder import (
    PeopleFinderTeamLeadersOrdering,
    PeopleFinderTeamType,
)


class PeopleFinderTeamMinimalResponse(Schema):
    slug: str = Field(alias="slug")
    name: str = Field(alias="name")
    abbreviation: Optional[str] = Field(alias="abbreviation")


class TeamRequest(Schema):
    slug: Optional[str] = None
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    description: Optional[str] = None
    leaders_ordering: Optional[PeopleFinderTeamLeadersOrdering] = None
    cost_code: Optional[str] = None
    team_type: Optional[PeopleFinderTeamType] = None
    parent_slug: Optional[str] = None


class CreateTeamRequest(TeamRequest):
    slug: str
    name: str
    parent_slug: str


class UpdateTeamRequest(TeamRequest): ...


class ParentSchema(PeopleFinderTeamMinimalResponse):
    depth: int


class PeopleFinderTeamHierarchyResponse(PeopleFinderTeamMinimalResponse):
    children: list["PeopleFinderTeamHierarchyResponse"] = Field(alias="children")


class PeopleFinderTeamResponse(PeopleFinderTeamMinimalResponse):
    parents: list[ParentSchema] = Field(alias="parents")


class PeopleFinderTeamUpdateResponse(PeopleFinderTeamMinimalResponse):
    description: Optional[str] = Field(alias="description")
    leaders_ordering: Optional[PeopleFinderTeamLeadersOrdering] = Field(
        alias="leaders_ordering"
    )
    cost_code: Optional[str] = Field(alias="cost_code")
    team_type: Optional[PeopleFinderTeamType] = Field(alias="team_type")
    parents: list[ParentSchema]
