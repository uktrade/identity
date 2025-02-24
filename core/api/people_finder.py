from ninja import Router

from core import services as core_services
from core.schemas import Error
from core.schemas.profiles import (
    PeopleFinderProfileRequestSchema,
    PeopleFinderProfileResponseSchema,
    ProfileMinimal,
)
from profiles.models.combined import Profile
from profiles.models.peoplefinder import PeopleFinderProfile


router = Router()
profile_router = Router()
router.add_router("person", profile_router)


# NB this is a placeholder to get the router running, it may need editing or deleting etc.
@profile_router.get(
    "{slug}",
    response={
        200: ProfileMinimal,
        404: Error,
    },
)
def get_profile(request, slug: str):
    """Just a demo, do not build against this"""
    try:
        return core_services.get_profile_by_slug(slug=slug)
    except Profile.DoesNotExist:
        return 404, {
            "message": "Unable to find user",
        }


@profile_router.put(
    "{slug}", response={200: PeopleFinderProfileResponseSchema, 404: Error}
)
def update_profile(
    request, slug: str, profile_request: PeopleFinderProfileRequestSchema
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
