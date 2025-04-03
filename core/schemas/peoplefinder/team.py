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


class CreateTeamRequest(Schema):
    slug: str
    name: str
    abbreviation: Optional[str] = None
    description: Optional[str] = None
    leaders_ordering: Optional[PeopleFinderTeamLeadersOrdering] = None
    cost_code: Optional[str] = None
    team_type: Optional[PeopleFinderTeamType] = None
    parent_slug: str


class ParentSchema(PeopleFinderTeamMinimalResponse):
    depth: int


class PeopleFinderTeamHierarchyResponse(PeopleFinderTeamMinimalResponse):
    children: list["PeopleFinderTeamHierarchyResponse"] = Field(alias="children")


class PeopleFinderTeamResponse(PeopleFinderTeamMinimalResponse):
    parents: list[ParentSchema] = Field(alias="parents")
