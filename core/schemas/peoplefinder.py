from dataclasses import dataclass
from typing import Optional

from ninja import Schema


@dataclass
class User:
    sso_email_id: str


@dataclass
class Email:
    value: str
    type: str | None = None
    primary: bool = False


class MinimalPeopleFinderProfile(Schema):
    # Basic Profile info
    slug: str
    first_name: str
    last_name: str
    user: Optional[User]  # ForeignKey to "user.User"
    preferred_first_name: Optional[str]
    pronouns: Optional[str]
    name_pronunciation: Optional[str]
    email: Optional[Email]  # ForeignKey to "profiles.Email"
    contact_email: Optional[Email]  # ForeignKey to "profiles.Email"
    primary_phone_number: Optional[str]
    secondary_phone_number: Optional[str]
    photo: Optional[str]  # ImageField is represented as a string (file path or URL)
    photo_small: Optional[
        str
    ]  # ImageField is represented as a string (file path or URL)
    grade: Optional[str]
