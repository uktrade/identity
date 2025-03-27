from ninja import Field, Schema


class PeopleFinderTeamSchema(Schema):
    slug: str = Field(alias="slug")
    name: str = Field(alias="name")
    abbreviation: str = Field(alias="abbreviation")


class ParentSchema(PeopleFinderTeamSchema):
    depth: int


class PeopleFinderTeamHierarchyResponse(PeopleFinderTeamSchema):
    children: list["PeopleFinderTeamHierarchyResponse"] = Field(alias="children")


class PeopleFinderTeamResponse(PeopleFinderTeamSchema):
    parents: list[ParentSchema] = Field(alias="parents")
