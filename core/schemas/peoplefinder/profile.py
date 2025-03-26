"""People Finder Schemas"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from ninja import Field, ModelSchema, Schema

from profiles.models import PeopleFinderProfile
from profiles.models.generic import Country, Grade, Profession, UkStaffLocation, Workday
from profiles.models.peoplefinder import (
    AdditionalRole,
    KeySkill,
    LearningInterest,
    RemoteWorking,
)


# Requests
class ProfileRequest(Schema):
    """
    People Finder profile request
    """

    sso_email_id: str
    became_inactive: Optional[datetime] = None
    edited_or_confirmed_at: Optional[datetime] = None
    login_count: Optional[int] = None
    first_name: Optional[str] = None
    preferred_first_name: Optional[str] = None
    last_name: Optional[str] = None
    pronouns: Optional[str] = None
    name_pronunciation: Optional[str] = None
    email_address: Optional[str] = None
    contact_email_address: Optional[str] = None
    primary_phone_number: Optional[str] = None
    secondary_phone_number: Optional[str] = None
    grade: Optional[Grade] = None
    manager_slug: Optional[str] = None
    not_employee: Optional[bool] = None
    workdays: Optional[List[Workday]] = None
    remote_working: Optional[RemoteWorking] = None
    usual_office_days: Optional[str] = None
    uk_office_location_id: Optional[str] = None
    location_in_building: Optional[str] = None
    international_building: Optional[str] = None
    country_id: Optional[str] = None
    professions: Optional[List[Profession]] = None
    additional_roles: Optional[list[AdditionalRole]] = None
    other_additional_roles: Optional[str] = None
    key_skills: Optional[List[KeySkill]] = None
    other_key_skills: Optional[str] = None
    learning_interests: Optional[List[LearningInterest]] = None
    other_learning_interests: Optional[str] = None
    fluent_languages: Optional[str] = None
    intermediate_languages: Optional[str] = None
    previous_experience: Optional[str] = None


class CreateProfileRequest(ProfileRequest):
    """People Finder profile creation request"""

    slug: str
    login_count: int = 0
    not_employee: bool = False
    country_id: str = "CTHMTC00260"


class UpdateProfileRequest(ProfileRequest):
    """People Finder profile update request"""

    ...


# Respones
class ProfileMinimalResponse(Schema):
    """
    Minimal People Finder profile.
    """

    slug: UUID
    sso_email_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    preferred_first_name: Optional[str]
    pronouns: Optional[str]
    name_pronunciation: Optional[str]
    email_address: str = Field(alias="email.address")
    contact_email_address: str = Field(alias="contact_email.address")
    primary_phone_number: Optional[str]
    secondary_phone_number: Optional[str]
    photo: Optional[str]  # ImageField is represented as a string (file path or URL)
    photo_small: Optional[
        str
    ]  # ImageField is represented as a string (file path or URL)
    grade: Optional[Grade]

    @staticmethod
    def resolve_sso_email_id(obj: PeopleFinderProfile):
        """
        Return the associated sso email id.
        """
        return obj.user.sso_email_id


class ProfileResponse(ProfileMinimalResponse):
    """Full People Finder profile"""

    became_inactive: Optional[datetime | None] = Field(alias="became_inactive")
    edited_or_confirmed_at: Optional[datetime] = Field(alias="edited_or_confirmed_at")
    login_count: Optional[int] = Field(alias="login_count")
    manager_slug: Optional[UUID] = Field(alias="manager.slug", default=None)
    not_employee: Optional[bool] = Field(alias="not_employee")
    workdays: Optional[List[Workday]] = Field(alias="workdays")
    remote_working: Optional[RemoteWorking] = Field(alias="remote_working")
    usual_office_days: Optional[str] = Field(alias="usual_office_days")
    uk_office_location_id: Optional[str] = Field(
        alias="uk_office_location.code", default=None
    )
    location_in_building: Optional[str] = Field(alias="location_in_building")
    international_building: Optional[str] = Field(alias="international_building")
    country_id: Optional[str] = Field(alias="country.reference_id")
    professions: Optional[List[Profession]] = Field(alias="professions")
    additional_roles: Optional[List[AdditionalRole]] = Field(alias="additional_roles")
    other_additional_roles: Optional[str] = Field(alias="other_additional_roles")
    key_skills: Optional[List[KeySkill]] = Field(alias="key_skills")
    other_key_skills: Optional[str] = Field(alias="other_key_skills")
    learning_interests: Optional[List[LearningInterest]] = Field(
        alias="learning_interests"
    )
    other_learning_interests: Optional[str] = Field(alias="other_learning_interests")
    fluent_languages: Optional[str] = Field(alias="fluent_languages")
    intermediate_languages: Optional[str] = Field(alias="intermediate_languages")
    previous_experience: Optional[str] = Field(alias="previous_experience")


# Reference data
class CountryResponse(ModelSchema):
    """
    Country response model
    """

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


class UkStaffLocationResponse(ModelSchema):
    """
    UK staff locations response model
    """

    class Meta:
        model = UkStaffLocation
        fields = [
            "code",
            "name",
            "organisation",
            "building_name",
        ]


class TextChoiceResponseSchema(Schema):
    key: str
    value: str
