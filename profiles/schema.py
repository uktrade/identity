from ninja import ModelSchema, Schema
from pydantic import Field

from profiles.models.people_finder import PeopleFinderProfile
from user.models.models import User

from .constants import BASIC, MINIMAL


class PeopleProfileIn(Schema):
    username: str = Field(alias="user.username")
    fav_program: str
    super_important: str


class PeopleProfileOutModel(ModelSchema):
    class Meta:
        model = PeopleFinderProfile
        fields = BASIC

    username: str = Field(alias="user.username")


class PeopleProfileOut(Schema):
    id: int
    username: str = Field(alias="user.username")
    fav_program: str
    super_important: str
