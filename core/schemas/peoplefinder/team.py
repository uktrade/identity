from ninja import Field, Schema


class PeopleFinderTeamSchema(Schema):
    slug: str = Field(alias="slug")
    name: str = Field(alias="name")
    abbreviation: str = Field(alias="abbreviation")
    children: list["PeopleFinderTeamSchema"]
