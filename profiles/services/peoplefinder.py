from django.forms import FileField

from profiles.models.generic import Country, UkStaffLocation
from profiles.models.peoplefinder import PeopleFinderProfile


def get_profile_completion(peoplefinder_profile):
    raise NotImplementedError


def update(
    people_finder_profile: PeopleFinderProfile,
    first_name: str | None,
    preferred_first_name: str | None,
    last_name: str | None,
    pronouns: str | None,
    name_pronunciation: str | None,
    email: str | None,
    contact_email: str | None,
    primary_phone_number: str | None,
    secondary_phone_number: str | None,
    photo: str | None,
    photo_small: str | None,
    grade: str | None,
    manager: PeopleFinderProfile | None,
    not_employee: bool | None,
    workdays: str | None,
    remote_working: str | None,
    usual_office_days: str | None,
    uk_office_location: UkStaffLocation | None,
    location_in_building: str | None,
    international_building: str | None,
    country: Country | None,
    professions: str | None,
    additional_roles: str | None,
    other_additional_roles: str | None,
    key_skills: str | None,
    other_key_skills: str | None,
    learning_interests: str | None,
    other_learning_interests: str | None,
    fluent_languages: str | None,
    intermediate_languages: str | None,
    previous_experience: str | None,
) -> None:
    fields_to_update = [
        first_name,
        preferred_first_name,
        last_name,
        pronouns,
        name_pronunciation,
        email,
        contact_email,
        primary_phone_number,
        secondary_phone_number,
        photo,
        photo_small,
        grade,
        manager,
        not_employee,
        workdays,
        remote_working,
        usual_office_days,
        uk_office_location,
        location_in_building,
        international_building,
        country,
        professions,
        additional_roles,
        other_additional_roles,
        key_skills,
        other_key_skills,
        learning_interests,
        other_learning_interests,
        fluent_languages,
        intermediate_languages,
        previous_experience,
    ]
    update_fields = []
    for field in fields_to_update:
        if field is not None:
            update_fields.append(str(field))
            people_finder_profile.field = field
    people_finder_profile.save(update_fields=update_fields)
