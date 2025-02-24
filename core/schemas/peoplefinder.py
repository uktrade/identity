from dataclasses import dataclass
from typing import Optional

from ninja import ModelSchema, Schema

from profiles.models import PeopleFinderProfile
from profiles.models.generic import Country


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
    sso_email_id: str
    preferred_first_name: Optional[str]
    pronouns: Optional[str]
    name_pronunciation: Optional[str]
    email: Optional[str]
    contact_email: Optional[str]
    primary_phone_number: Optional[str]
    secondary_phone_number: Optional[str]
    photo: Optional[str]  # ImageField is represented as a string (file path or URL)
    photo_small: Optional[
        str
    ]  # ImageField is represented as a string (file path or URL)
    grade: Optional[str]

    @staticmethod
    def resolve_slug(obj: PeopleFinderProfile):
        return str(obj.slug)

    @staticmethod
    def resolve_sso_email_id(obj: PeopleFinderProfile):
        return obj.user.sso_email_id

    @staticmethod
    def resolve_email(obj: PeopleFinderProfile):
        return obj.email.address

    @staticmethod
    def resolve_contact_email(obj: PeopleFinderProfile):
        return obj.contact_email.address


class CountrySchema(ModelSchema):
    class Meta:
        model = Country
        fields = [
            "reference_id",
            "name",
            "type",
            "iso_1_code",
            "iso_2_code",
            "iso_3_code",
            "overseas_region",
            "start_date",
            "end_date",
        ]
