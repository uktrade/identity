from ninja import ModelSchema
from profiles.models.peoplefinder import (
    PeopleFinderProfile,
    PeopleFinderTeam,
    PeopleFinderProfileTeam,
    PeopleFinderTeamTree,
)


class PeopleFinderProfileSchema(ModelSchema):
    class Meta:
        model = PeopleFinderProfile
        fields = "__all__"


class PeopleFinderTeamSchema(ModelSchema):
    class Meta:
        model = PeopleFinderTeam
        fields = "__all__"


class PeopleFinderProfileTeamSchema(ModelSchema):
    class Meta:
        model = PeopleFinderProfileTeam
        fields = "__all__"


class PeopleFinderTeamTreeSchema(ModelSchema):
    class Meta:
        model = PeopleFinderTeamTree
        fields = "__all__"
