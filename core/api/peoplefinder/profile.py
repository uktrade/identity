from django import forms
from django.core.files.base import File
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseNotAllowed
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from storages.backends.s3 import S3File
from ninja import File, Router, Schema, Form
from ninja.files import UploadedFile
from PIL import Image
import json

from core import services as core_services
from core.schemas import Error
from core.schemas.peoplefinder.profile import (
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
router.add_router("people", profile_router)
router.add_router("reference", reference_router)


@profile_router.get(
    "{slug}",
    response={
        200: ProfileMinimalResponse,
        404: Error,
    },
)
def get_profile(request, slug: str):
    """Endpoint to return a full peoplefinder profile record"""
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
    """Endpoint to create a new people finder profile"""
    try:
        combined_profile = core_services.get_identity_by_id(
            id=profile_request.sso_email_id
        )

        workdays_list: list[Workday] | None = None
        if profile_request.workdays:
            workdays_list = [Workday(workday) for workday in profile_request.workdays]

        professions_list: list[Profession] | None = None
        if profile_request.professions:
            professions_list = [
                Profession(profession) for profession in profile_request.professions
            ]

        learning_interests_list: list[LearningInterest] | None = None
        if profile_request.learning_interests:
            learning_interests_list = [
                LearningInterest(learning_interest)
                for learning_interest in profile_request.learning_interests
            ]

        key_skills_list: list[KeySkill] | None = None
        if profile_request.key_skills:
            key_skills_list = [
                KeySkill(key_skill) for key_skill in profile_request.key_skills
            ]

        additional_roles_list: list[AdditionalRole] | None = None
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
            grade=(
                None if profile_request.grade is None else Grade(profile_request.grade)
            ),
            manager_slug=profile_request.manager_slug,
            not_employee=profile_request.not_employee,
            workdays=None if workdays_list is None else workdays_list,
            remote_working=(
                None
                if profile_request.remote_working is None
                else RemoteWorking(profile_request.remote_working)
            ),
            usual_office_days=profile_request.usual_office_days,
            uk_office_location_id=profile_request.uk_office_location_id,
            location_in_building=profile_request.location_in_building,
            international_building=profile_request.international_building,
            country_id=profile_request.country_id,
            professions=None if professions_list is None else professions_list,
            additional_roles=(
                None if additional_roles_list is None else additional_roles_list
            ),
            key_skills=None if key_skills_list is None else key_skills_list,
            other_key_skills=profile_request.other_key_skills,
            learning_interests=(
                None if learning_interests_list is None else learning_interests_list
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
    """Endpoint to update an existing people finder profile"""
    try:
        combined_profile = core_services.get_identity_by_id(
            id=profile_request.sso_email_id
        )

        workdays_list: Unset | list[Workday]
        if profile_request.workdays is None:
            workdays_list = UNSET
        else:
            workdays_list = [Workday(workday) for workday in profile_request.workdays]

        professions_list: Unset | list[Profession]
        if profile_request.professions is None:
            professions_list = UNSET
        else:
            professions_list = [
                Profession(profession) for profession in profile_request.professions
            ]

        learning_interests_list: Unset | list[LearningInterest]
        if profile_request.learning_interests is None:
            learning_interests_list = UNSET
        else:
            learning_interests_list = [
                LearningInterest(learning_interest)
                for learning_interest in profile_request.learning_interests
            ]

        key_skills_list: Unset | list[KeySkill]
        if profile_request.key_skills is None:
            key_skills_list = UNSET
        else:
            key_skills_list = [
                KeySkill(key_skill) for key_skill in profile_request.key_skills
            ]

        additional_roles_list: Unset | list[AdditionalRole]
        if profile_request.additional_roles is None:
            additional_roles_list = UNSET
        else:
            additional_roles_list = [
                AdditionalRole(additional_role)
                for additional_role in profile_request.additional_roles
            ]

        core_services.update_peoplefinder_profile(
            profile=combined_profile,
            slug=slug,
            is_active=combined_profile.is_active,  # TODO: Cam/Marcel to discuss, shouldn't the first step just be to store PF data and not change it's behaviour/purpose?
            became_inactive=(
                UNSET
                if profile_request.became_inactive is None
                else profile_request.became_inactive
            ),
            edited_or_confirmed_at=(
                UNSET
                if profile_request.edited_or_confirmed_at is None
                else profile_request.edited_or_confirmed_at
            ),
            login_count=profile_request.login_count,
            first_name=(
                UNSET
                if profile_request.first_name is None
                else profile_request.first_name
            ),
            last_name=profile_request.last_name if profile_request.last_name else UNSET,
            preferred_first_name=(
                UNSET
                if profile_request.preferred_first_name is None
                else profile_request.preferred_first_name
            ),
            pronouns=(
                UNSET if profile_request.pronouns is None else profile_request.pronouns
            ),
            name_pronunciation=(
                UNSET
                if profile_request.name_pronunciation is None
                else profile_request.name_pronunciation
            ),
            email_address=(
                UNSET
                if profile_request.email_address is None
                else profile_request.email_address
            ),
            contact_email_address=(
                UNSET
                if profile_request.contact_email_address is None
                else profile_request.contact_email_address
            ),
            primary_phone_number=(
                UNSET
                if profile_request.primary_phone_number is None
                else profile_request.primary_phone_number
            ),
            secondary_phone_number=(
                UNSET
                if profile_request.secondary_phone_number is None
                else profile_request.secondary_phone_number
            ),
            grade=(
                UNSET if profile_request.grade is None else Grade(profile_request.grade)
            ),
            manager_slug=(
                UNSET
                if profile_request.manager_slug is None
                else profile_request.manager_slug
            ),
            not_employee=profile_request.not_employee,
            workdays=workdays_list,
            remote_working=(
                UNSET
                if profile_request.remote_working is None
                else RemoteWorking(profile_request.remote_working)
            ),
            usual_office_days=(
                UNSET
                if profile_request.usual_office_days is None
                else profile_request.usual_office_days
            ),
            uk_office_location_id=(
                UNSET
                if profile_request.uk_office_location_id is None
                else profile_request.uk_office_location_id
            ),
            location_in_building=(
                UNSET
                if profile_request.location_in_building is None
                else profile_request.location_in_building
            ),
            international_building=(
                UNSET
                if profile_request.international_building is None
                else profile_request.international_building
            ),
            country_id=profile_request.country_id,
            professions=professions_list,
            additional_roles=additional_roles_list,
            other_additional_roles=(
                UNSET
                if profile_request.other_additional_roles is None
                else profile_request.other_additional_roles
            ),
            key_skills=key_skills_list,
            other_key_skills=(
                UNSET
                if profile_request.other_key_skills is None
                else profile_request.other_key_skills
            ),
            learning_interests=learning_interests_list,
            other_learning_interests=(
                UNSET
                if profile_request.other_learning_interests is None
                else profile_request.other_learning_interests
            ),
            fluent_languages=(
                UNSET
                if profile_request.fluent_languages is None
                else profile_request.fluent_languages
            ),
            intermediate_languages=(
                UNSET
                if profile_request.intermediate_languages is None
                else profile_request.intermediate_languages
            ),
            previous_experience=(
                UNSET
                if profile_request.previous_experience is None
                else profile_request.previous_experience
            ),
        )
        return 200, core_services.get_profile_by_slug(slug=slug)
    except Profile.DoesNotExist:
        return 404, {"message": "Profile does not exist"}
    except PeopleFinderProfile.DoesNotExist:
        return 404, {"message": "People finder profile does not exist"}


# @profile_router.post(
#     path="{slug}/photo",
#     response={
#         200: ProfileResponse,  # @TODO custom minimal response ?
#         404: Error,
#         422: Error,
#     },
# )

class PhotoForm(forms.Form):
    image = forms.ImageField()

    def clean(self):
        cleaned_data = super().clean()
        self.validate_photo(cleaned_data["image"])
        return cleaned_data

    def validate_photo(self, image):
        if not hasattr(image, "image"):
            return

        if image.image.width < 500:
            self.add_error("image", ValidationError("Width is less than 500px"))

        if image.image.height < 500:
            self.add_error("image", ValidationError("Height is less than 500px"))

        # 8mb in bytes
        if image.size > 1024 * 1024 * 8:
            self.add_error("image", ValidationError("File size is greater than 8MB"))

@csrf_exempt
def upload_profile_photo(request, slug: str):
    """
    Endpoint to upload a new profile photo for the given profile
    """
    print("CALLED")
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST", "DELETE"])

    try:
        profile = core_services.get_peoplefinder_profile_by_slug(slug=slug)
    except PeopleFinderProfile.DoesNotExist:
        return HttpResponseNotFound(json.dumps({
            "message": "Unable to find people finder profile",
        }))

    form = PhotoForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponseBadRequest(json.dumps(form.errors))

    # image = request.FILES["file"]

    # try:
    #     im = Image.open(image)
    #     im.verify()
    # except:
    #     return 422, {
    #         "message": "Not a valid image file",
    #     }

    # photo: File = image.open()
    profile.photo.delete()
    profile.photo = form.cleaned_data["image"]
    profile.save()
    return HttpResponse(ProfileResponse.from_orm(profile).json())


# @profile_router.delete(
#     path="{slug}/photo",
#     response={
#         200: ProfileResponse,
#         404: Error,
#     },
# )
# def delete_profile_photo(request, slug: str):
#     """
#     Endpoint to delete a profile photo for the given profile
#     """
#     try:
#         profile = core_services.get_peoplefinder_profile_by_slug(slug=slug)
#     except PeopleFinderProfile.DoesNotExist:
#         return 404, {
#             "message": "Unable to find people finder profile",
#         }

#     profile.photo.delete()
#     return profile


@reference_router.get(
    "countries",
    response={
        200: list[CountryResponse],
        500: Error,
    },
)
def get_countries(request) -> tuple[int, list[Country] | dict]:
    try:
        # Get a list of all countries
        return 200, core_services.get_countries()
    except Exception as unknown_error:
        return 500, {"message": f"Could not get Countries, reason: {unknown_error}"}


@reference_router.get(
    "uk_staff_locations",
    response={
        200: list[UkStaffLocationResponse],
        500: Error,
    },
)
def get_uk_staff_locations(request) -> tuple[int, list[UkStaffLocation] | dict]:
    try:
        return 200, core_services.get_uk_staff_locations()
    except Exception as unknown_error:
        return 500, {
            "message": f"Could not get UK staff locations, reason: {unknown_error}"
        }


@reference_router.get(
    "remote_working",
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
    "workdays",
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
    "learning_interests",
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
    "professions",
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


@reference_router.get(
    "grades",
    response={
        200: list[TextChoiceResponseSchema],
        500: Error,
    },
)
def get_grades(request):
    try:
        grades = [
            {"key": key, "value": value} for key, value in core_services.get_grades()
        ]
        return 200, grades
    except Exception as unknown_error:
        return 500, {"message": f"Could not get grades, reason: {unknown_error}"}


@reference_router.get(
    "key_skills",
    response={
        200: list[TextChoiceResponseSchema],
        500: Error,
    },
)
def get_key_skills(request):
    try:
        key_skills = [
            {"key": key, "value": value}
            for key, value in core_services.get_key_skills()
        ]
        return 200, key_skills
    except Exception as unknown_error:
        return 500, {"message": f"Could not get key skills, reason: {unknown_error}"}


@reference_router.get(
    "additional_roles",
    response={
        200: list[TextChoiceResponseSchema],
        500: Error,
    },
)
def get_additional_roles(request):
    try:
        additional_roles = [
            {"key": key, "value": value}
            for key, value in core_services.get_additional_roles()
        ]
        return 200, additional_roles
    except Exception as unknown_error:
        return 500, {
            "message": f"Could not get additional roles, reason: {unknown_error}"
        }
