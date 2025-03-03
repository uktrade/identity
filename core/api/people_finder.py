from ninja import Router

from core import services as core_services
from core.schemas import Error
from core.schemas.peoplefinder import (
    CountryResponse,
    CreateProfileRequest,
    ProfileMinimalResponse,
    ProfileResponse,
    TextChoiceResponseSchema,
    UkStaffLocationResponse,
    UpdateProfileRequest,
)
from profiles.exceptions import ProfileExists
from profiles.models.combined import Profile
from profiles.models.generic import Country, UkStaffLocation
from profiles.models.peoplefinder import PeopleFinderProfile


router = Router()
profile_router = Router()
reference_router = Router()
router.add_router("person", profile_router)
router.add_router("reference", reference_router)


@profile_router.get(
    "{slug}",
    response={
        200: ProfileMinimalResponse,
        404: Error,
    },
)
def get_profile(request, slug: str):
    """Optimised, low-flexibility endpoint to return a minimal peoplefinder profile record"""
    try:
        return core_services.get_peoplefinder_profile_by_slug(slug=slug)
    except PeopleFinderProfile.DoesNotExist:
        return 404, {
            "message": "Unable to find people finder profile",
        }


@profile_router.post("", response={201: ProfileResponse, 404: Error, 409: Error})
def create_profile(
    request, profile_request: CreateProfileRequest
) -> tuple[int, PeopleFinderProfile | dict]:
    try:
        combined_profile = core_services.get_identity_by_id(
            id=profile_request.sso_email_id
        )

        core_services.create_peoplefinder_profile(
            slug=profile_request.slug,
            sso_email_id=profile_request.sso_email_id,
            became_inactive=profile_request.became_inactive,
            edited_or_confirmed_at=profile_request.edited_or_confirmed_at,
            login_count=profile_request.login_count,
            first_name=profile_request.first_name,
            preferred_first_name=profile_request.preferred_first_name,
            last_name=profile_request.last_name,
            pronouns=profile_request.pronouns,
            name_pronunciation=profile_request.name_pronunciation,
            email_address=profile_request.email_address,
            contact_email_address=profile_request.contact_email_address,
            primary_phone_number=profile_request.primary_phone_number,
            secondary_phone_number=profile_request.secondary_phone_number,
            photo=profile_request.photo,
            photo_small=profile_request.photo_small,
            grade=profile_request.grade,
            manager_slug=profile_request.manager_slug,
            workdays=profile_request.workdays,
            remote_working=profile_request.remote_working,
            usual_office_days=profile_request.usual_office_days,
            uk_office_location_id=profile_request.uk_office_location_id,
            location_in_building=profile_request.location_in_building,
            international_building=profile_request.international_building,
            country_id=profile_request.country_id,
            professions=profile_request.professions,
            additional_roles=profile_request.additional_roles,
            key_skills=profile_request.key_skills,
            other_key_skills=profile_request.other_key_skills,
            learning_interests=profile_request.learning_interests,
            other_learning_interests=profile_request.other_learning_interests,
            fluent_languages=profile_request.fluent_languages,
            intermediate_languages=profile_request.intermediate_languages,
            previous_experience=profile_request.previous_experience,
        )
        return 201, core_services.get_profile_by_slug(slug=profile_request.slug)
    except Profile.DoesNotExist:
        return 404, {"message": "Profile does not exist"}
    except ProfileExists:
        return 409, {
            "message": "A people finder profile for this user has already been created"
        }


@profile_router.put("{slug}", response={200: ProfileResponse, 404: Error})
def update_profile(
    request, slug: str, profile_request: UpdateProfileRequest
) -> tuple[int, PeopleFinderProfile | dict]:
    try:
        combined_profile = core_services.get_identity_by_id(
            id=profile_request.sso_email_id
        )
        core_services.update_peoplefinder_profile(
            profile=combined_profile,
            slug=slug,
            is_active=combined_profile.is_active,
            became_inactive=profile_request.became_inactive,
            edited_or_confirmed_at=profile_request.edited_or_confirmed_at,
            login_count=profile_request.login_count,
            first_name=profile_request.first_name,
            last_name=profile_request.last_name,
            preferred_first_name=profile_request.preferred_first_name,
            pronouns=profile_request.pronouns,
            name_pronunciation=profile_request.name_pronunciation,
            email_address=profile_request.email_address,
            contact_email_address=profile_request.contact_email_address,
            primary_phone_number=profile_request.primary_phone_number,
            secondary_phone_number=profile_request.secondary_phone_number,
            photo=profile_request.photo,
            photo_small=profile_request.photo_small,
            grade=profile_request.grade,
            manager_slug=profile_request.manager_slug,
            not_employee=profile_request.not_employee,
            workdays=profile_request.workdays,
            remote_working=profile_request.remote_working,
            usual_office_days=profile_request.usual_office_days,
            uk_office_location_id=profile_request.uk_office_location_id,
            location_in_building=profile_request.location_in_building,
            international_building=profile_request.international_building,
            country_id=profile_request.country_id,
            professions=profile_request.professions,
            additional_roles=profile_request.additional_roles,
            other_additional_roles=profile_request.other_additional_roles,
            key_skills=profile_request.key_skills,
            other_key_skills=profile_request.other_key_skills,
            learning_interests=profile_request.learning_interests,
            other_learning_interests=profile_request.other_learning_interests,
            fluent_languages=profile_request.fluent_languages,
            intermediate_languages=profile_request.intermediate_languages,
            previous_experience=profile_request.previous_experience,
        )
        return 200, core_services.get_profile_by_slug(slug=slug)
    except Profile.DoesNotExist:
        return 404, {"message": "Profile does not exist"}
    except PeopleFinderProfile.DoesNotExist:
        return 404, {"message": "People finder profile does not exist"}


@reference_router.get(
    "countries/",
    response={
        200: list[CountryResponse],
        404: Error,
    },
)
def get_countries(request) -> tuple[int, list[Country] | dict]:
    try:
        # Get a list of all countries
        countries = core_services.get_countries()
        if len(countries) > 0:
            return 200, countries
        else:
            return 404, {"message": "No Countries to display"}
    except Exception as unknown_error:
        return 404, {"message": f"Could not get Countries, reason: {unknown_error}"}


@reference_router.get(
    "uk_staff_locations/",
    response={
        200: list[UkStaffLocationResponse],
        404: Error,
    },
)
def get_uk_staff_locations(request) -> tuple[int, list[UkStaffLocation] | dict]:
    try:
        uk_staff_locations = core_services.get_uk_staff_locations()
        if len(uk_staff_locations) > 0:
            return 200, uk_staff_locations
        else:
            return 404, {"message": "No UK staff location to display"}
    except Exception as unknown_error:
        return 404, {
            "message": f"Could not get UK staff locations, reason: {unknown_error}"
        }


@reference_router.get(
    "remote_working/",
    response={
        200: list[TextChoiceResponseSchema],
        500: Error,
    },
)
def get_remote_working(request):
    try:
        remote_working_options = [
            {"key": key, "value": value}
            for key, value in core_services.get_remote_working()
        ]
        return 200, remote_working_options
    except Exception as unknown_error:
        return 500, {
            "message": f"Could not get remote working options, reason: {unknown_error}"
        }


@reference_router.get(
    "workdays/",
    response={
        200: list[TextChoiceResponseSchema],
        500: Error,
    },
)
def get_workdays(request):
    try:
        workday_options = [
            {"key": key, "value": value} for key, value in core_services.get_workdays()
        ]
        return 200, workday_options
    except Exception as unknown_error:
        return 500, {"message": f"Could not get workdays, reason: {unknown_error}"}


@reference_router.get(
    "learning_interests/",
    response={
        200: list[TextChoiceResponseSchema],
        500: Error,
    },
)
def get_learning_interests(request):
    try:
        learning_interest_options = [
            {"key": key, "value": value}
            for key, value in core_services.get_learning_interests()
        ]
        return 200, learning_interest_options
    except Exception as unknown_error:
        return 500, {
            "message": f"Could not get learning interests, reason: {unknown_error}"
        }


@reference_router.get(
    "professions/",
    response={
        200: list[TextChoiceResponseSchema],
        500: Error,
    },
)
def get_professions(request):
    try:
        professions = [
            {"key": key, "value": value}
            for key, value in core_services.get_professions()
        ]
        return 200, professions
    except Exception as unknown_error:
        return 500, {"message": f"Could not get professions, reason: {unknown_error}"}
