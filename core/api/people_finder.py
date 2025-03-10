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
from profiles.models.generic import Country, Grade, Profession, UkStaffLocation, Workday
from profiles.models.peoplefinder import (
    AdditionalRole,
    KeySkill,
    LearningInterest,
    PeopleFinderProfile,
    RemoteWorking,
)
from profiles.types import UNSET, Unset


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

        workdays_list: list[Workday] = []
        if profile_request.workdays:
            workdays_list = [Workday(workday) for workday in profile_request.workdays]

        professions_list: list[Profession] = []
        if profile_request.professions:
            professions_list = [
                Profession(profession) for profession in profile_request.professions
            ]

        learning_interests_list: list[LearningInterest] = []
        if profile_request.learning_interests:
            learning_interests_list = [
                LearningInterest(learning_interest)
                for learning_interest in profile_request.learning_interests
            ]

        key_skills_list: list[KeySkill] = []
        if profile_request.key_skills:
            key_skills_list = [
                KeySkill(key_skill) for key_skill in profile_request.key_skills
            ]

        additional_roles_list: list[AdditionalRole] = []
        if profile_request.additional_roles:
            additional_roles_list = [
                AdditionalRole(additional_role)
                for additional_role in profile_request.additional_roles
            ]

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
            grade=Grade(profile_request.grade) if profile_request.grade else None,
            manager_slug=profile_request.manager_slug,
            not_employee=profile_request.not_employee,
            workdays=workdays_list if workdays_list else None,
            remote_working=(
                RemoteWorking(profile_request.remote_working)
                if profile_request.remote_working
                else None
            ),
            usual_office_days=profile_request.usual_office_days,
            uk_office_location_id=profile_request.uk_office_location_id,
            location_in_building=profile_request.location_in_building,
            international_building=profile_request.international_building,
            country_id=profile_request.country_id,
            professions=professions_list if professions_list else None,
            additional_roles=additional_roles_list if additional_roles_list else None,
            key_skills=key_skills_list if key_skills_list else None,
            other_key_skills=profile_request.other_key_skills,
            learning_interests=(
                learning_interests_list if learning_interests_list else None
            ),
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

        workdays_list: Unset | list[Workday]
        if not profile_request.workdays:
            workdays_list = UNSET
        elif profile_request.workdays:
            workdays_list = [Workday(workday) for workday in profile_request.workdays]

        professions_list: Unset | list[Profession]
        if not profile_request.professions:
            professions_list = UNSET
        elif profile_request.professions:
            professions_list = [
                Profession(profession) for profession in profile_request.professions
            ]

        learning_interests_list: Unset | list[LearningInterest]
        if not profile_request.learning_interests:
            learning_interests_list = UNSET
        elif profile_request.learning_interests:
            learning_interests_list = [
                LearningInterest(learning_interest)
                for learning_interest in profile_request.learning_interests
            ]

        key_skills_list: Unset | list[KeySkill]
        if not profile_request.key_skills:
            key_skills_list = UNSET
        elif profile_request.key_skills:
            key_skills_list = [
                KeySkill(key_skill) for key_skill in profile_request.key_skills
            ]

        additional_roles_list: Unset | list[AdditionalRole]
        if not profile_request.additional_roles:
            additional_roles_list = UNSET
        elif profile_request.additional_roles:
            additional_roles_list = [
                AdditionalRole(additional_role)
                for additional_role in profile_request.additional_roles
            ]

        core_services.update_peoplefinder_profile(
            profile=combined_profile,
            slug=slug,
            is_active=combined_profile.is_active,  # TODO: Cam/Marcel to discuss, shouldn't the first step just be to store PF data and not change it's behaviour/purpose?
            became_inactive=(
                profile_request.became_inactive
                if profile_request.became_inactive
                else UNSET
            ),
            edited_or_confirmed_at=(
                profile_request.edited_or_confirmed_at
                if profile_request.edited_or_confirmed_at
                else UNSET
            ),
            login_count=profile_request.login_count,
            first_name=(
                profile_request.first_name if profile_request.first_name else UNSET
            ),
            last_name=profile_request.last_name if profile_request.last_name else UNSET,
            preferred_first_name=(
                profile_request.preferred_first_name
                if profile_request.preferred_first_name
                else UNSET
            ),
            pronouns=profile_request.pronouns if profile_request.pronouns else UNSET,
            name_pronunciation=(
                profile_request.name_pronunciation
                if profile_request.name_pronunciation
                else UNSET
            ),
            email_address=(
                profile_request.email_address
                if profile_request.email_address
                else UNSET
            ),
            contact_email_address=(
                profile_request.contact_email_address
                if profile_request.contact_email_address
                else UNSET
            ),
            primary_phone_number=(
                profile_request.primary_phone_number
                if profile_request.primary_phone_number
                else UNSET
            ),
            secondary_phone_number=(
                profile_request.secondary_phone_number
                if profile_request.secondary_phone_number
                else UNSET
            ),
            photo=(
                profile_request.photo if profile_request.preferred_first_name else UNSET
            ),
            photo_small=profile_request.photo_small if profile_request.photo else UNSET,
            grade=Grade(profile_request.grade) if profile_request.grade else UNSET,
            manager_slug=(
                profile_request.manager_slug if profile_request.manager_slug else UNSET
            ),
            not_employee=profile_request.not_employee,
            workdays=workdays_list,
            remote_working=(
                RemoteWorking(profile_request.remote_working)
                if profile_request.remote_working
                else UNSET
            ),
            usual_office_days=(
                profile_request.usual_office_days
                if profile_request.usual_office_days
                else UNSET
            ),
            uk_office_location_id=(
                profile_request.uk_office_location_id
                if profile_request.uk_office_location_id
                else UNSET
            ),
            location_in_building=(
                profile_request.location_in_building
                if profile_request.location_in_building
                else UNSET
            ),
            international_building=(
                profile_request.international_building
                if profile_request.international_building
                else UNSET
            ),
            country_id=profile_request.country_id,
            professions=professions_list,
            additional_roles=additional_roles_list,
            other_additional_roles=(
                profile_request.other_additional_roles
                if profile_request.other_additional_roles
                else UNSET
            ),
            key_skills=key_skills_list,
            other_key_skills=(
                profile_request.other_key_skills
                if profile_request.other_key_skills
                else UNSET
            ),
            learning_interests=learning_interests_list,
            other_learning_interests=(
                profile_request.other_learning_interests
                if profile_request.other_learning_interests
                else UNSET
            ),
            fluent_languages=(
                profile_request.fluent_languages
                if profile_request.fluent_languages
                else UNSET
            ),
            intermediate_languages=(
                profile_request.intermediate_languages
                if profile_request.intermediate_languages
                else UNSET
            ),
            previous_experience=(
                profile_request.previous_experience
                if profile_request.previous_experience
                else UNSET
            ),
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
