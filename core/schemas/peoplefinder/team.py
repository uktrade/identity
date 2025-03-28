from ninja import Field, Schema

from profiles.models.peoplefinder import (
    PeopleFinderTeamLeadersOrdering,
    PeopleFinderTeamType,
)


class PeopleFinderTeamSchema(Schema):
    slug: str = Field(alias="slug")
    name: str = Field(alias="name")
    abbreviation: str = Field(alias="abbreviation")


class CreateTeamRequest(Schema):
    slug: str = Field(alias="slug")
    name: str = Field(alias="name")
    abbreviation: str = Field(alias="abbreviation")
    description: str = Field(alias="description")
    leaders_ordering: PeopleFinderTeamLeadersOrdering = Field(alias="leaders_ordering")
    cost_code: str = Field(alias="cost_code")
    team_type: PeopleFinderTeamType = Field(alias="team_type")
    parent_slug: str


class ParentSchema(PeopleFinderTeamSchema):
    depth: int


class PeopleFinderTeamHierarchyResponse(PeopleFinderTeamSchema):
    children: list["PeopleFinderTeamHierarchyResponse"] = Field(alias="children")


class PeopleFinderTeamResponse(PeopleFinderTeamSchema):
    parents: list[ParentSchema] = Field(alias="parents")
