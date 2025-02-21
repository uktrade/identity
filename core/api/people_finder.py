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
def get_user(request, slug: str):
    """Just a demo, do not build against this"""
    try:
        return core_services.get_profile_by_slug(slug=slug)
    except Profile.DoesNotExist:
        return 404, {
            "message": "Unable to find user",
        }


@profile_router.put(
    "{slug}", response={200: PeopleFinderProfileResponseSchema, 400: Error}
)
def update_user(
    request, slug: str, peoplefinder_profile: PeopleFinderProfileRequestSchema
) -> tuple[int, PeopleFinderProfile | dict]:
    try:
        profile = core_services.get_identity_by_id(id=peoplefinder_profile.sso_email_id)
        core_services.update_peoplefinder_profile(
            profile=profile,
            slug=slug,
            is_active=profile.is_active,
            became_inactive=peoplefinder_profile.became_inactive,
            edited_or_confirmed_at=peoplefinder_profile.edited_or_confirmed_at,
            login_count=peoplefinder_profile.login_count,
            first_name=peoplefinder_profile.first_name,
            last_name=peoplefinder_profile.last_name,
            preferred_first_name=peoplefinder_profile.preferred_first_name,
            pronouns=peoplefinder_profile.pronouns,
            name_pronunciation=peoplefinder_profile.name_pronunciation,
            email_address=peoplefinder_profile.email_address,
            contact_email_address=peoplefinder_profile.contact_email_address,
            primary_phone_number=peoplefinder_profile.primary_phone_number,
            secondary_phone_number=peoplefinder_profile.secondary_phone_number,
            photo=peoplefinder_profile.photo,
            photo_small=peoplefinder_profile.photo_small,
            grade=peoplefinder_profile.grade,
            manager_slug=peoplefinder_profile.manager_slug,
            not_employee=peoplefinder_profile.not_employee,
            workdays=peoplefinder_profile.workdays,
            remote_working=peoplefinder_profile.remote_working,
            usual_office_days=peoplefinder_profile.usual_office_days,
            uk_office_location_id=peoplefinder_profile.uk_office_location_id,
            location_in_building=peoplefinder_profile.location_in_building,
            international_building=peoplefinder_profile.international_building,
            country_id=peoplefinder_profile.country_id,
            professions=peoplefinder_profile.professions,
            additional_roles=peoplefinder_profile.additional_roles,
            other_additional_roles=peoplefinder_profile.other_additional_roles,
            key_skills=peoplefinder_profile.key_skills,
            other_key_skills=peoplefinder_profile.other_key_skills,
            learning_interests=peoplefinder_profile.learning_interests,
            other_learning_interests=peoplefinder_profile.other_learning_interests,
            fluent_languages=peoplefinder_profile.fluent_languages,
            intermediate_languages=peoplefinder_profile.intermediate_languages,
            previous_experience=peoplefinder_profile.previous_experience,
        )
        return 200, core_services.get_profile_by_slug(slug=slug)
    except Profile.DoesNotExist:
        return 404, {"message": "Profile does not exist"}
