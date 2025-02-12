from profiles.models.generic import Country, UkStaffLocation
from profiles.models.peoplefinder import PeopleFinderProfile
from profiles.types import UNSET, Unset


def get_profile_completion(peoplefinder_profile):
    # TODO: Implement get_profile_completion() funtion.
    raise NotImplementedError


def update(
    peoplefinder_profile: PeopleFinderProfile,
    first_name: str,
    last_name: str,
    preferred_first_name: str | Unset | None,
    pronouns: str | Unset | None,
    name_pronunciation: str | Unset | None,
    email: str | Unset | None,
    contact_email: str | Unset | None,
    primary_phone_number: str | Unset | None,
    secondary_phone_number: str | Unset | None,
    photo: str | Unset | None,
    photo_small: str | Unset | None,
    grade: str | Unset | None,
    manager: PeopleFinderProfile | Unset | None,
    not_employee: bool | Unset | None,
    workdays: list[str],
    remote_working: str | Unset | None,
    usual_office_days: str | Unset | None,
    uk_office_location: UkStaffLocation | Unset | None,
    location_in_building: str | Unset | None,
    international_building: str | Unset | None,
    country: Country,
    professions: list[str],
    additional_roles: list[str],
    other_additional_roles: str | Unset | None,
    key_skills: list[str],
    other_key_skills: str | Unset | None,
    learning_interests: list[str],
    other_learning_interests: str | Unset | None,
    fluent_languages: str | Unset | None,
    intermediate_languages: str | Unset | None,
    previous_experience: str | Unset | None,
) -> None:
    
    update_fields = []
    if first_name:
        update_fields.append("first_name")
        peoplefinder_profile.first_name = first_name
    if last_name:
        update_fields.append("last_name")
        peoplefinder_profile.last_name = last_name
    if preferred_first_name is not None:
        if preferred_first_name is UNSET:
            peoplefinder_profile.preferred_first_name = None
        else:
            peoplefinder_profile.preferred_first_name = preferred_first_name
        update_fields.append("preferred_first_name")
            
    if pronouns is not None:
        update_fields.append("pronouns")
        peoplefinder_profile.pronouns = pronouns
    if name_pronunciation is not None:
        update_fields.append("name_pronunciation")
        peoplefinder_profile.name_pronunciation = name_pronunciation
    if email is not None:
        update_fields.append("email")
        peoplefinder_profile.email = email
    if contact_email is not None:
        update_fields.append("contact_email")
        peoplefinder_profile.contact_email = contact_email
    if primary_phone_number is not None:
        update_fields.append("primary_phone_number")
        peoplefinder_profile.primary_phone_number = primary_phone_number
    if secondary_phone_number is not None:
        update_fields.append("secondary_phone_number")
        peoplefinder_profile.secondary_phone_number = secondary_phone_number
    if photo is not None:
        update_fields.append("photo")
        peoplefinder_profile.photo = photo
    
    peoplefinder_profile.save(update_fields=update_fields)
