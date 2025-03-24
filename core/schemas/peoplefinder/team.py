from ninja import Field, Schema


class PeopleFinderTeamTreeResponse(Schema):
    parent: str = Field(alias="parent.slug")
    child: str = Field(alias="child.slug")
    depth: int = Field(alias="depth")
