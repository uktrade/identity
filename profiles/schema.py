from ninja import Schema
from pydantic import Field

from user.models.models import User


class PeopleProfileIn(Schema):
    username: str = Field(alias="user.username")
    fav_program: str
    super_important: str


class PeopleProfileOut(Schema):
    id: int
    username: str = Field(alias="user.username")
    fav_program: str
    super_important: str
