from profiles.models.generic import Country, UkStaffLocation
from profiles.models.peoplefinder import PeopleFinderProfile


def get_profile_completion(peoplefinder_profile):
    # TODO: Implement get_profile_completion() funtion.
    raise NotImplementedError


def update(
    peoplefinder_profile: PeopleFinderProfile,
    first_name: str,
    preferred_first_name: str | None,
    last_name: str,
    pronouns: str | None,
    name_pronunciation: str | None,
    email: str | None,
    contact_email: str | None,
    primary_phone_number: str | None,
    secondary_phone_number: str | None,
    photo: str | None,
    photo_small: str | None,
    grade: str,
    manager: PeopleFinderProfile | None,
    not_employee: bool | None,
    workdays: list[str],
    remote_working: str | None,
    usual_office_days: str | None,
    uk_office_location: UkStaffLocation | None,
    location_in_building: str | None,
    international_building: str | None,
    country: Country,
    professions: list[str],
    additional_roles: list[str],
    other_additional_roles: str | None,
    key_skills: list[str],
    other_key_skills: str | None,
    learning_interests: list[str],
    other_learning_interests: str | None,
    fluent_languages: str | None,
    intermediate_languages: str | None,
    previous_experience: str | None,
) -> None:

    fields_to_update = {
        "first_name": first_name,
        "preferred_first_name": preferred_first_name,
        "last_name": last_name,
        "pronouns": pronouns,
        "name_pronunciation": name_pronunciation,
        "email": email,
        "contact_email": contact_email,
        "primary_phone_number": primary_phone_number,
        "secondary_phone_number": secondary_phone_number,
        "photo": photo,
        "photo_small": photo_small,
        "grade": grade,
        "manager": manager,
        "not_employee": not_employee,
        "workdays": workdays,
        "remote_working": remote_working,
        "usual_office_days": usual_office_days,
        "uk_office_location": uk_office_location,
        "location_in_building": location_in_building,
        "international_building": international_building,
        "country": country,
        "professions": professions,
        "additional_roles": additional_roles,
        "other_additional_roles": other_additional_roles,
        "key_skills": key_skills,
        "other_key_skills": other_key_skills,
        "learning_interests": learning_interests,
        "other_learning_interests": other_learning_interests,
        "fluent_languages": fluent_languages,
        "intermediate_languages": intermediate_languages,
        "previous_experience": previous_experience,
    }
    update_fields = []
    for field, value in fields_to_update.items():
        update_fields.append(field)
        setattr(peoplefinder_profile, field, value)
    peoplefinder_profile.save(update_fields=update_fields)
