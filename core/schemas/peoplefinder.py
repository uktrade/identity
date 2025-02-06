from ninja import ModelSchema

from profiles.models.peoplefinder import (
    PeopleFinderProfile,
    PeopleFinderProfileTeam,
    PeopleFinderTeam,
    PeopleFinderTeamTree,
)


class PeopleFinderProfileSchema(ModelSchema):
    class Meta:
        model = PeopleFinderProfile
        exclude = []


class PeopleFinderTeamSchema(ModelSchema):
    class Meta:
        model = PeopleFinderTeam
        exclude = []


class PeopleFinderProfileTeamSchema(ModelSchema):
    class Meta:
        model = PeopleFinderProfileTeam
        exclude = []


class PeopleFinderTeamTreeSchema(ModelSchema):
    class Meta:
        model = PeopleFinderTeamTree
        exclude = []
