from datetime import datetime
from typing import Optional

from profiles.models.generic import Country, Email, Grade, UkStaffLocation
from profiles.models.peoplefinder import PeopleFinderProfile
from user.models import User


def get_profile_completion(peoplefinder_profile):
    raise NotImplementedError


def create(
    slug: str,
    sso_email_id: str,
    became_inactive: datetime,
    edited_or_confirmed_at: datetime,
    login_count: int,
    first_name: Optional[str] = None,
    preferred_first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    pronouns: Optional[str] = None,
    name_pronunciation: Optional[str] = None,
    email_address: Optional[str] = None,
    contact_email_address: Optional[str] = None,
    primary_phone_number: Optional[str] = None,
    secondary_phone_number: Optional[str] = None,
    photo: Optional[str] = None,
    photo_small: Optional[str] = None,
    grade_id: Optional[str] = None,
    manager_id: Optional[str] = None,
    workdays: Optional[list[str]] = None,
    remote_working: Optional[list[str]] = None,
    usual_office_days: Optional[list[str]] = None,
    uk_office_location_id: Optional[str] = None,
    location_in_building: Optional[str] = None,
    international_building: Optional[str] = None,
    country_id: Optional[str] = None,
    professions: Optional[list[str]] = None,
    additional_roles: Optional[str] = None,
    key_skills: Optional[list[str]] = None,
    other_key_skills: Optional[str] = None,
    learning_interests: Optional[list[str]] = None,
    other_learning_interests: Optional[str] = None,
    fluent_languages: Optional[str] = None,
    intermediate_languages: Optional[str] = None,
    previous_experience: Optional[str] = None,
) -> PeopleFinderProfile:

    user = User.objects.get(pk=sso_email_id)
    

    peoplefinder_profile: dict[str, any] = {
        "slug": slug,
        "user": user,
        "is_active": user.is_active,
        "became_inactive": became_inactive,
        "edited_or_confirmed_at": edited_or_confirmed_at,
        "login_count": login_count,
        "first_name": first_name,
        "preferred_first_name": preferred_first_name,
        "last_name": last_name,
        "pronouns": pronouns,
        "name_pronunciation": name_pronunciation,
        "email": set_email_details(address=email_address),
        "contact_email": set_email_details(address=contact_email_address),
        "primary_phone_number": primary_phone_number,
        "secondary_phone_number": secondary_phone_number,
        "photo": photo,
        "photo_small": photo_small,
        "grade": set_grade(grade_id=grade_id),
        "manager": set_manager(manager_id=manager_id),
        "workdays": workdays,
        "remote_working": remote_working,
        "usual_office_days": usual_office_days,
        "uk_office_location": set_uk_office_location(
            uk_office_location_id=uk_office_location_id
        ),
        "location_in_building": location_in_building,
        "international_building": international_building,
        "country": set_country(country_id=country_id),
        "professions": professions,
        "additional_roles": additional_roles,
        "key_skills": key_skills,
        "other_key_skills": other_key_skills,
        "learning_interests": learning_interests,
        "other_learning_interests": other_learning_interests,
        "fluent_languages": fluent_languages,
        "intermediate_languages": intermediate_languages,
        "previous_experience": previous_experience,
    }

    PeopleFinderProfile.objects.create(**peoplefinder_profile)


###############################################################
# Email data methods
###############################################################
def set_email_details(address: str) -> Email:
    if address is not None and len(address.strip()) > 0:
        return Email.objects.get_or_create(address=address)
    return None


def set_grade(grade_id: str) -> Grade:
    if grade_id is not None:
        return Grade.objects.get(pk=grade_id)
    return None


def set_manager(manager_id: str) -> User:
    # TODO Talk about this, should this be UUID or SSO.
    if manager_id is not None:
        return User.objects.get(pk=manager_id)
    return None


def set_uk_office_location(uk_office_location_id: str) -> UkStaffLocation:
    if uk_office_location_id is not None:
        return UkStaffLocation.objects.get(pk=uk_office_location_id)
    return None


def set_country(country_id: str):
    if country_id is not None:
        return Country.objects.get(pk=country_id)
    return None
