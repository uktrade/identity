from datetime import datetime
from typing import List, Optional
from uuid import UUID

from ninja import Field, ModelSchema, Schema

from profiles.models.combined import Profile
from profiles.models.generic import UkStaffLocation


class ProfileMinimal(ModelSchema):
    id: str = Field(alias="sso_email_id")

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "primary_email",
            "contact_email",
            "emails",
        ]


class PeopleFinderProfileRequestSchema(Schema):
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
    photo: Optional[str] = None
    photo_small: Optional[str] = None
    grade: Optional[str] = None
    manager_slug: Optional[str] = None
    not_employee: Optional[bool] = None
    workdays: Optional[List[str]] = None
    remote_working: Optional[str] = None
    usual_office_days: Optional[str] = None
    uk_office_location_id: Optional[str] = None
    location_in_building: Optional[str] = None
    international_building: Optional[str] = None
    country_id: Optional[str] = None
    professions: Optional[List[str]] = None
    additional_roles: Optional[List[str]] = None
    other_additional_roles: Optional[str] = None
    key_skills: Optional[List[str]] = None
    other_key_skills: Optional[str] = None
    learning_interests: Optional[List[str]] = None
    other_learning_interests: Optional[str] = None
    fluent_languages: Optional[str] = None
    intermediate_languages: Optional[str] = None
    previous_experience: Optional[str] = None


class PeopleFinderProfileResponseSchema(Schema):
    became_inactive: Optional[datetime | None] = Field(alias="became_inactive")
    edited_or_confirmed_at: Optional[datetime] = Field(alias="edited_or_confirmed_at")
    login_count: Optional[int] = Field(alias="login_count")
    first_name: Optional[str] = Field(alias="first_name")
    preferred_first_name: Optional[str] = Field(alias="preferred_first_name")
    last_name: Optional[str] = Field(alias="last_name")
    pronouns: Optional[str] = Field(alias="pronouns")
    name_pronunciation: Optional[str] = Field(alias="name_pronunciation")
    email_address: Optional[str] = Field(alias="email.address")
    contact_email_address: Optional[str] = Field(alias="contact_email.address")
    primary_phone_number: Optional[str] = Field(alias="primary_phone_number")
    secondary_phone_number: Optional[str] = Field(alias="secondary_phone_number")
    photo: Optional[str] = Field(alias="photo")
    photo_small: Optional[str] = Field(alias="photo_small")
    grade: Optional[str] = Field(alias="grade")
    manager_slug: Optional[UUID] = Field(alias="manager.slug")
    not_employee: Optional[bool] = Field(alias="not_employee")
    workdays: Optional[List[str]] = Field(alias="workdays")
    remote_working: Optional[str] = Field(alias="remote_working")
    usual_office_days: Optional[str] = Field(alias="usual_office_days")
    uk_office_location_id: Optional[str] = Field(alias="uk_office_location.code")
    location_in_building: Optional[str] = Field(alias="location_in_building")
    international_building: Optional[str] = Field(alias="international_building")
    country_id: Optional[str] = Field(alias="country.reference_id")
    professions: Optional[List[str]] = Field(alias="professions")
    additional_roles: Optional[List[str]] = Field(alias="additional_roles")
    other_additional_roles: Optional[str] = Field(alias="other_additional_roles")
    key_skills: Optional[List[str]] = Field(alias="key_skills")
    other_key_skills: Optional[str] = Field(alias="other_key_skills")
    learning_interests: Optional[List[str]] = Field(alias="learning_interests")
    other_learning_interests: Optional[str] = Field(alias="other_learning_interests")
    fluent_languages: Optional[str] = Field(alias="fluent_languages")
    intermediate_languages: Optional[str] = Field(alias="intermediate_languages")
    previous_experience: Optional[str] = Field(alias="previous_experience")


class UkStaffLocationSchema(ModelSchema):
    class Meta:
        model = UkStaffLocation
        fields = [
            "code",
            "name",
            "organisation",
            "building_name",
        ]
