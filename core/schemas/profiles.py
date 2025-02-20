import datetime
from typing import List, Optional

from ninja import Field, ModelSchema, Schema

from profiles.models.combined import Profile
from profiles.models.generic import Country, UkStaffLocation
from profiles.models.peoplefinder import PeopleFinderProfile


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


class UserSchema(Schema):
    sso_email_id: str = Field(alias="user.sso_email_id")


class PeopleFinderProfileSchema(Schema):
    # Basic Profile info
    slug: str = Field(alias="slug")
    user: Optional[UserSchema]  # ForeignKey to "user.User"
    first_name: str = Field(alias="first_name")
    preferred_first_name: Optional[str] = Field(alias="preferred_first_name")
    last_name: str = Field(alias="last_name")
    pronouns: Optional[str] = Field(alias="pronouns")
    name_pronunciation: Optional[str] = Field(alias="name_pronounciation")
    email: Optional[str] = Field(alias="email")
    contact_email: Optional[str] = Field(alias="contact_email")
    primary_phone_number: Optional[str] = Field(alias="primary_phone_number")
    secondary_phone_number: Optional[str] = Field(alias="secondary_phone_number")
    photo: Optional[str] = Field(alias="photo")
    photo_small: Optional[str] = Field(alias="photo_small")

    # HR information
    grade: Optional[str] = Field(alias="grade")
    manager: Optional[PeopleFinderProfile] = Field(alias="manager")
    not_employee: bool = Field(alias="not_employee")

    # Working patterns
    workdays: Optional[List[str]] = Field(alias="workdays")
    remote_working: Optional[str] = Field(alias="remote_working")
    usual_office_days: Optional[str] = Field(alias="usual_office_days")
    uk_office_location: Optional[UkStaffLocation] = Field(alias="uk_office_location")
    location_in_building: Optional[str] = Field(alias="location_in_building")
    international_building: Optional[str] = Field(alias="international_building")
    country: Optional[Country] = Field(alias="country")

    # Supplementary info
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

    # Metadata and status
    edited_or_confirmed_at: datetime = Field(alias="edited_or_confirmed_at")
    login_count: Optional[int] = Field(alias="login_count")
    profile_completion: Optional[int] = Field(alias="profile_completion")
    ical_token: Optional[str] = Field(alias="ical_token")
